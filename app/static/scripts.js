document.addEventListener('DOMContentLoaded', function() {
    const products = document.querySelectorAll('.product-item');
    const productsPerPage = 16;
    const totalPages = Math.ceil(products.length / productsPerPage);
    let currentPage = 1;

    function showPage(pageNumber) {
        const startIndex = (pageNumber - 1) * productsPerPage;
        const endIndex = startIndex + productsPerPage;
        products.forEach(function(product, index) {
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
            paginationContainer.innerHTML = ''; // 清空現有按鈕

            // 創建當前顯示的頁碼範圍
            const startPage = Math.max(1, currentPage - 1);
            const endPage = Math.min(totalPages, startPage + 2);

            for (let i = startPage; i <= endPage; i++) {
                paginationContainer.appendChild(createPageButton(i));
            }

            // 增加下一頁按鈕
            if (endPage < totalPages) {
                const nextPageButton = createPageButton(endPage + 1);
                nextPageButton.textContent = '»';
                paginationContainer.appendChild(nextPageButton);
            }
        }

        updatePaginationButtons();
        document.body.appendChild(paginationContainer);
    }

    showPage(currentPage); // 初始化顯示第 1 頁
    createPaginationButtons();

    // 新增的代碼
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();  // 阻止表單的默認提交行為

            var url = form.action;

            fetch(url, {
                method: 'POST',
                body: new FormData(form)  // 使用表單數據創建一個新的 FormData 對象
            })
            .then(response => response.json())
            .then(data => {
                alert('產品已成功加入購物車');  // 顯示成功消息
                // 這裡可以添加其他的代碼，例如更新購物車的數量等
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
