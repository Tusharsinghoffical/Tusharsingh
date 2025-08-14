// Admin JavaScript for product management
document.addEventListener('DOMContentLoaded', function() {
    // Add low stock warning
    const stockInputs = document.querySelectorAll('.field-stock input');
    stockInputs.forEach(input => {
        const checkStock = () => {
            if (parseInt(input.value) < 10) {
                input.classList.add('low-stock');
            } else {
                input.classList.remove('low-stock');
            }
        };
        input.addEventListener('input', checkStock);
        checkStock();
    });

    // Price formatting
    const priceInputs = document.querySelectorAll('.field-price input');
    priceInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });

    // Image preview on file selection
    const imageInput = document.querySelector('.field-image input[type="file"]');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('.field-image_preview img');
                    if (preview) {
                        preview.src = e.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Slug auto-generation
    const nameInput = document.querySelector('.field-name input');
    const slugInput = document.querySelector('.field-slug input');
    if (nameInput && slugInput) {
        nameInput.addEventListener('input', function() {
            if (!slugInput.dataset.manual) {
                slugInput.value = nameInput.value
                    .toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/^-+|-+$/g, '');
            }
        });
        
        slugInput.addEventListener('input', function() {
            this.dataset.manual = true;
        });
    }
});
