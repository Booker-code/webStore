document.addEventListener('DOMContentLoaded', function() {
    const products = document.querySelectorAll('.product-item');
    const productsPerPage = 16;
    const productsArray = Array.from(products); 
    const totalPages = Math.ceil(productsArray.length / productsPerPage);
    let currentPage = 1;

    function showPage(pageNumber) {
        const startIndex = (pageNumber - 1) * productsPerPage;
        const endIndex = startIndex + productsPerPage;
        productsArray.forEach(function(product, index) {
            if (index >= startIndex && index < endIndex) {
                product.style.display = 'block';
            } else {
                product.style.display = 'none';
            }
        });
    }

    function createPaginationButtons() {
        const paginationContainer = document.createElement('div');
        paginationContainer.classList.add('pagination');

        function createPageButton(pageNumber) {
            const pageButton = document.createElement('button');
            pageButton.textContent = pageNumber;
            pageButton.addEventListener('click', function() {
                currentPage = pageNumber;
                showPage(currentPage);
                updatePaginationButtons();
            });
            return pageButton;
        }

        function updatePaginationButtons() {
            paginationContainer.innerHTML = ''; 

            const startPage = Math.max(1, currentPage - 1);
            const endPage = Math.min(totalPages, startPage + 2);

            for (let i = startPage; i <= endPage; i++) {
                paginationContainer.appendChild(createPageButton(i));
            }

            if (endPage < totalPages) {
                const nextPageButton = createPageButton(endPage + 1);
                nextPageButton.textContent = '»';
                paginationContainer.appendChild(nextPageButton);
            }
        }

        updatePaginationButtons();
        document.body.appendChild(paginationContainer);
    }

    showPage(currentPage); 
    createPaginationButtons();

    
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();  

            const url = form.action;

            fetch(url, {
                method: 'POST',
                body: new FormData(form)  
            })
            .then(response => response.json())
            .then(data => {
                alert('产品已成功加入购物车'); 
                
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
