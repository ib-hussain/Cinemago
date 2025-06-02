const carousel = document.querySelector('.carousel');
const leftBtn = document.querySelector('.left-btn');
const rightBtn = document.querySelector('.right-btn');

let scrollAmount = 0;
const step = document.querySelector('.movie').offsetWidth + 15; // Includes gap

function autoScroll() {
    if (scrollAmount >= carousel.scrollWidth - carousel.clientWidth) {
        scrollAmount = 0;
        carousel.style.transition = 'none'; 
    } else {
        scrollAmount += step;
        carousel.style.transition = 'transform 0.3s ease-in-out';
    }
    carousel.style.transform = `translateX(-${scrollAmount}px)`;
}

setInterval(autoScroll, 1500);

rightBtn.addEventListener('click', () => {
    autoScroll();
});

leftBtn.addEventListener('click', () => {
    if (scrollAmount <= 0) {
        scrollAmount = carousel.scrollWidth - carousel.clientWidth;
        carousel.style.transition = 'none';
    } else {
        scrollAmount -= step;
        carousel.style.transition = 'transform 0.3s ease-in-out';
    }
    carousel.style.transform = `translateX(-${scrollAmount}px)`;
});
