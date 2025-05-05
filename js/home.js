document.addEventListener('DOMContentLoaded', function () {
    const carousel = document.querySelector('.movie-carousel');
    const cards = document.querySelectorAll('.movie-card');
    const leftArrow = document.querySelector('.left-arrow');
    const rightArrow = document.querySelector('.right-arrow');
    let currentIndex = 2; // Start with "The Fallen Idol" as active
  
    function updateActiveCard() {
      cards.forEach((card, index) => {
        if (index === currentIndex) {
          card.classList.add('active-card');
        } else {
          card.classList.remove('active-card');
        }
      });
  
      // Removed scrollIntoView to stop auto-scroll on load
      // Scroll will only happen on arrow clicks now
    }
  
    leftArrow.addEventListener('click', () => {
      if (currentIndex > 0) {
        currentIndex--;
        cards[currentIndex].scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'center'
        });
        updateActiveCard();
      }
    });
  
    rightArrow.addEventListener('click', () => {
      if (currentIndex < cards.length - 1) {
        currentIndex++;
        cards[currentIndex].scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'center'
        });
        updateActiveCard();
      }
    });
  
    // Initialize card highlighting without auto-scroll
    updateActiveCard();
  });
  