// Обработчик отправки формы для добавления товара
var addProductForm = document.getElementById('addProductForm');
if (addProductForm) {
    addProductForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Предотвращаем отправку формы по умолчанию
        var formData = new FormData(this);
        fetch('/add_product', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                console.log('accept adding product');
                $('#addProductModal').modal('hide');
                updateTable();
            } else {
                console.error('Error adding product');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
} else {
    console.error("Add product form not found.");
}

// Обработчик отправки формы для добавления локации
var addLocationForm = document.getElementById('addLocationForm');
if (addLocationForm) {
    addLocationForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Предотвращаем отправку формы по умолчанию
        var formData = new FormData(this);
        fetch('/add_location', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                console.log('Location added successfully');
                $('#addLocationModal').modal('hide');
                updateTable()
            } else {
                console.error('Error adding location');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
} else {
    console.error("Add location form not found.");
}

// Обработчик события изменения текста в поле поиска
var searchInput = document.getElementById('searchInput');
if (searchInput) {
    searchInput.addEventListener('input', function(event) {
        var searchTerm = event.target.value.trim(); // Получаем значение введенного текста и удаляем начальные и конечные пробелы
        
        // Выполняем запрос на сервер для поиска товаров
        fetch('/search_product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                searchTerm: searchTerm
            })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to search products');
            }
        })
        .then(data => {
            // Обновляем таблицу с полученными данными
            updateInventoryTable(data);
        })
        .catch(error => {
            console.error('Error searching products:', error);
        });
    });
} else {
    console.error("Search input not found.");
}

// Обработчик события для обновления количества товара при изменении значения поля ввода
document.addEventListener('change', function(event) {
    if (event.target.matches('input[type="number"]')) {
        var inputElement = event.target;
        var productIdInput = inputElement.parentElement.querySelector('.productId');
        var locationIdInput = inputElement.parentElement.querySelector('.locationId');

        if (productIdInput && locationIdInput) {
            var productId = productIdInput.value;
            var locationId = locationIdInput.value;
            var newQuantity = inputElement.value;

            fetch('/update_quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    productId: productId,
                    locationId: locationId,
                    newQuantity: newQuantity
                })
            })
            .then(response => {
                if (response.ok) {
                    console.log('Quantity updated successfully');
                    updateTable()
                } else {
                    console.error('Error updating quantity');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        } else {
            console.error('Product ID or Location ID input not found');
        }
    }
});

// Обработчик нажатия кнопки "Remove from Inventory"
var removeFromInventoryButtons = document.querySelectorAll('.remove-from-inventory');
if (removeFromInventoryButtons) {
    removeFromInventoryButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var productId = button.dataset.productId; // Получаем ID продукта из атрибута data-product-id кнопки

            // Отображаем модальное окно для подтверждения удаления
            $('#confirmDeleteModal').modal('show');

            // Обработчик нажатия кнопки "Delete" в модальном окне
            var confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
            confirmDeleteBtn.addEventListener('click', function() {
                // Отправляем запрос на сервер для удаления продукта
                fetch('/delete_product', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        productId: productId
                    })
                })
                .then(response => {
                    if (response.ok) {
                        console.log('Product successfully deleted');
                        $('#confirmDeleteModal').modal('hide');
                        updateTable();
                    } else {
                        console.error('Error deleting product');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
    });
}

// Обработчик события для сортировки по выбранной локации
$('.sort-by-location').change(function() {
    var selectedLocation = $(this).val();
    if (selectedLocation === "") {
        // Если выбрана опция "All Locations", отправляем запрос на сервер для получения всей таблицы
        fetch('/data')
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to fetch all data');
                }
            })
            .then(data => {
                // Обновляем таблицу с полученными данными
                updateInventoryTable(data);
            })
            .catch(error => {
                console.error('Error fetching all data:', error);
            });
    } else {
        // В противном случае отправляем запрос на сервер с выбранной локацией для фильтрации
        $.ajax({
            url: '/filter_by_location',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                locationId: selectedLocation
            }),
            success: function(response) {
                updateInventoryTable(response);
            },
            error: function(xhr, status, error) {
                alert(xhr.responseJSON.error);
            }
        });
    }
});

$('.sort-by-price, .sort-by-quantity, .sort-by-name, .sort-by-description').click(function() {
    var sortField = $(this).data('sort-by'); // Получаем поле для сортировки
    var sortOrder = $(this).data('sort-order') || 'asc';
    sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';

    $.ajax({
        url: '/sort_by_field',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            sortField: sortField, // Используйте sortField вместо field
            order: sortOrder
        }),
        success: function(response) {
            updateInventoryTable(response);
            // Обновляем атрибут data-sort-order для следующего клика
            $(this).data('sort-order', sortOrder);
        }.bind(this), // Привязываем контекст выполнения функции обратного вызова
        error: function(xhr, status, error) {
            alert(xhr.responseJSON.error);
        }
    });
});


function updateInventoryTable(data) {
    // Очистить текущее содержимое таблицы
    var tbody = document.querySelector('tbody');
    tbody.innerHTML = '';
    console.log(data);

    // Заполнить таблицу с новыми данными
    data.forEach(item => {
        var newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${item.name}</td>
            <td>${item.description}</td>
            <td>${item.price}</td>
            <td>${item.location}</td>
            <td>${item.quantity}</td>
            <td>
                <button class="btn btn-primary" data-toggle="modal" data-target="#addProductModal">Add to Inventory</button>
                <button class="btn btn-danger mt-2 remove-from-inventory" data-toggle="modal" data-target="#deleteConfirmProductModal" data-product-id="{{ item.product_id }}">Remove from Inventory</button>
            </td>
        `;
        tbody.appendChild(newRow);
    });
}

// Функция для обновления данных таблицы
function updateTable() {
    fetch('/')
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to update inventory table');
        }
    })
    .then(data => {
        // Обновляем таблицу с полученными данными
        updateInventoryTable(data);
    })
    .catch(error => {
        console.error('Error updating inventory table:', error);
    });
}





