// goto button

// window.addEventListener("scroll", function() {
//     let navbar = document.getElementById("goto");
//     if (window.scrollY > 100) { // Change color after 50px scroll
//         navbar.style.display="block";
//     } else {
//         navbar.style.display="none";
//     }
// });

//loader



// Show loader immediately as script runs
  document.addEventListener("DOMContentLoaded", () => {
    showLoader(); // Show instantly
  });

  // Define loader functions
  function showLoader() {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = "flex";
  }

  function hideLoader() {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = "none";
  }

  // Hide loader once everything is fully loaded
  window.addEventListener("load", () => {
    setTimeout(hideLoader, 1000); // Delay to allow loader to be visible
  });

  // Optional: simulate loading manually (e.g. after clicking a link)
  function simulateLoading() {
    showLoader();
    setTimeout(hideLoader, 2000);
  }

  // Optional: for <a> links you want to trigger loader on click
  // document.querySelectorAll("a").forEach(link => {
  //   link.addEventListener("click", function (e) {
  //     const href = this.getAttribute("href");
  //     if (href && !href.startsWith("#") && !href.startsWith("javascript:")) {
  //       showLoader();
  //     }
  //   });
  // });


// navbar

document.addEventListener("DOMContentLoaded", () => {
  const navbar = document.getElementById("navbar");
  const toggler = document.querySelector(".navbar-toggler");

  const handleScroll = () => {
    if (window.scrollY > 10) {
      navbar.classList.add("navbar-white");
      toggler.classList.add("navbar-dark-icon");
    } else {
      navbar.classList.remove("navbar-white");
      toggler.classList.remove("navbar-dark-icon");
    }
  };

  // Listen for scroll and touch movement
  window.addEventListener("scroll", handleScroll);
  window.addEventListener("touchmove", handleScroll);
});


// home slider 

document.addEventListener("DOMContentLoaded", function () {
  const slides = document.querySelectorAll('.slider-sections');
  const paginationContainer = document.querySelector('.pagination-dots');
  let current = 0;
  let startX = 0;
  let endX = 0;

  // Create pagination dots
  slides.forEach((_, index) => {
    const dot = document.createElement('span');
    dot.classList.add('dot');
    if (index === 0) dot.classList.add('active');
    dot.addEventListener('click', () => {
      current = index;
      showSlide(current);
    });
    paginationContainer.appendChild(dot);
  });

  const dots = document.querySelectorAll('.dot');

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.remove('active');
      if (i === index) {
        slide.classList.add('active');
      }
    });

    dots.forEach((dot, i) => {
      dot.classList.remove('active');
      if (i === index) {
        dot.classList.add('active');
      }
    });
  }

  function nextSlide() {
    current = (current + 1) % slides.length;
    showSlide(current);
  }

  function prevSlide() {
    current = (current - 1 + slides.length) % slides.length;
    showSlide(current);
  }

  setInterval(nextSlide, 5000); // Auto-slide

  // Touch support
  const sliderBox = document.querySelector('.sliders-box');
  sliderBox.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
  });

  sliderBox.addEventListener('touchend', (e) => {
    endX = e.changedTouches[0].clientX;
    handleSwipe();
  });

  function handleSwipe() {
    const diff = startX - endX;
    if (Math.abs(diff) > 50) { // swipe threshold
      if (diff > 0) {
        nextSlide(); // swipe left
      } else {
        prevSlide(); // swipe right
      }
    }
  }
});


//<!-- JS to Auto Rotate Active --> for professional-list li

document.addEventListener("DOMContentLoaded", function () {
  const items = document.querySelectorAll(".professional-list li");
  let current = 0;

  if (!items.length) return; // ✅ No <li>? Don't run script

  function rotateActive() {
    items.forEach(item => item.classList.remove("active"));

    const currentItem = items[current];
    if (currentItem) {
      currentItem.classList.add("active");
    }

    current = (current + 1) % items.length;
  }

  setInterval(rotateActive, 3000); // Rotate every 3 seconds
});



document.addEventListener('DOMContentLoaded', () => {
  const steps = document.querySelectorAll('.step');
  const stepsWrapper = document.querySelector('.steps-wrapper');
  const section = document.getElementById('project-steps');

  let currentStep = 0;
  const totalSteps = steps.length;

  setInterval(() => {
    if (currentStep === totalSteps) {
      steps.forEach(step => step.classList.remove('active'));
      currentStep = 0;
      return; // 🛑 stop this tick and wait for the next interval
    }

    const activeStep = steps[currentStep];
    if (!activeStep) return; // safety check

    activeStep.classList.add('active');

    const sectionRect = section.getBoundingClientRect();
    const inViewport = sectionRect.top < window.innerHeight && sectionRect.bottom > 0;

    if (window.innerWidth < 1025 && inViewport) {
      activeStep.scrollIntoView({
        behavior: 'smooth',
        inline: 'center',
        block: 'nearest'
      });
    }

    currentStep++;
  }, 3000);
});




document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".stats-grid .stat-number");
  const container = document.querySelector(".stats-grid");
  let activated = false;

  // Exit early if container doesn't exist to avoid error
  if (!container) return;

  const animateCounter = (counter, target, duration = 2000) => {
    const start = 0;
    const startTime = performance.now();
    const hasPlus = counter.innerText.includes('+');

    const update = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1); // Clamp between 0 and 1
      const easedProgress = 1 - Math.pow(1 - progress, 3); // Ease-out cubic
      const currentCount = Math.floor(start + easedProgress * (target - start));
      counter.innerText = currentCount + (hasPlus ? '+' : '');

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        counter.innerText = target + (hasPlus ? '+' : '');
      }
    };

    requestAnimationFrame(update);
  };

  window.addEventListener("scroll", () => {
    const scrollPosition = window.pageYOffset;
    const triggerPoint = container.offsetTop - window.innerHeight + 100;

    if (scrollPosition > triggerPoint && !activated) {
      counters.forEach(counter => {
        const target = parseInt(counter.dataset.count);
        animateCounter(counter, target);
      });
      activated = true;
    }

    // Reset (optional)
    if ((scrollPosition < container.offsetTop - 500 || scrollPosition === 0) && activated) {
      counters.forEach(counter => {
        counter.innerText = '0' + (counter.innerText.includes('+') ? '+' : '');
      });
      activated = false;
    }
  });
});


 //testimonals slider 

document.addEventListener('DOMContentLoaded', function () {
  const track = document.getElementById('testimonialTrack');
  const items = track.querySelectorAll('.testimonial-item');
  const itemCount = items.length;
  let index = 0;

  function slideTestimonials() {
    index = (index + 1) % itemCount;
    track.style.transform = `translateX(-${index * 10}%)`;
  }

  setInterval(slideTestimonials, 3000); // change every 3 seconds
});


//blog swiper

document.addEventListener('DOMContentLoaded', function () {
  var swiper = new Swiper('.blog-swiper', {
    loop: true,
    centeredSlides: true,
    autoplay: {
      delay: 2000,
      disableOnInteraction: false,
      reverseDirection: false
    },
    slidesPerView: 1,
    spaceBetween: 20,
    breakpoints: {
      768: {
        slidesPerView: 2,
        centeredSlides: true
      },
      992: {
        slidesPerView: 3,
        centeredSlides: true
      }
    },
    pagination: {
      el: '.swiper-pagination',
      clickable: true
    }
  });

  // Pause on hover
  const swiperContainer = document.querySelector('.swiper.blog-swiper');
  swiperContainer.addEventListener('mouseover', function () {
    swiper.autoplay.stop();
  });
  swiperContainer.addEventListener('mouseout', function () {
    swiper.autoplay.start();
  });
});



// blog slider 

function scrollSlider(direction) {
  const slider = document.getElementById('featuredSlider');
  const scrollAmount = 320; // Approx width of one card + gap

  slider.scrollBy({
    left: direction * scrollAmount,
    behavior: 'smooth'
  });
}





  document.addEventListener("DOMContentLoaded", function () {
    const counters = document.querySelectorAll(".counter");
    let animated = false;

    function animateCounter(el, to, decimal) {
      const duration = 2000; // 2 seconds
      const start = 0;
      const isDecimal = decimal || false;
      const step = (timestamp, startTime, startVal) => {
        const progress = Math.min((timestamp - startTime) / duration, 1);
        const value = startVal + (to - startVal) * progress;
        el.innerText = isDecimal ? value.toFixed(1) : Math.floor(value);
        if (progress < 1) {
          requestAnimationFrame(ts => step(ts, startTime, startVal));
        }
      };
      requestAnimationFrame(ts => step(ts, ts, start));
    }

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !animated) {
          counters.forEach(counter => {
            const target = parseFloat(counter.getAttribute("data-count"));
            const isDecimal = counter.dataset.decimal === "true";
            animateCounter(counter, target, isDecimal);
          });
          animated = true; // prevent re-triggering
        }
      });
    }, { threshold: 0.5 });

    const section = document.querySelector(".counter-section");
    observer.observe(section);
  });

document.addEventListener("DOMContentLoaded", function () {
    const items = document.querySelectorAll(".timeline-item");

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("show");
        }
      });
    }, {
      threshold: 0.4,
    });

    items.forEach(item => observer.observe(item));
  });




document.querySelectorAll('.dropdown').forEach(drop => {
  drop.addEventListener('show.bs.dropdown', function () {
    const menu = this.querySelector('.dropdown-menu');
    menu.style.animation = 'fadeSlideDown 0.4s ease forwards';
  });
  drop.addEventListener('hide.bs.dropdown', function () {
    const menu = this.querySelector('.dropdown-menu');
    menu.style.animation = 'none';
  });
});

//animation

document.addEventListener("DOMContentLoaded", function () {
    const elements = document.querySelectorAll(".auto-show-left");

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate");
          observer.unobserve(entry.target); // Remove if you only want the animation once
        }
      });
    }, {
      threshold: 0.2  // Roughly like "view(80% 10%)"
    });

    elements.forEach(el => observer.observe(el));
  });

document.addEventListener("DOMContentLoaded", function () {
  const elements = document.querySelectorAll(".auto-show-up");

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && entry.target instanceof HTMLElement) {
        entry.target.classList.add("animate");
        // Now the observer keeps watching — animation can replay
      } else {
        // Optionally remove the class when it's out of view
        entry.target.classList.remove("animate");
      }
    });
  }, {
    threshold: 0.2
  });

  elements.forEach(el => {
    if (el instanceof HTMLElement) {
      observer.observe(el);
    }
  });
});



// chat bot 

function toggleChat() {
  const chatBox = document.getElementById("chat-widget");
  chatBox.style.display = chatBox.style.display === "none" || !chatBox.style.display ? "block" : "none";
}

function handleOption(option) {
  alert(`You clicked: ${option}`);
  // You can handle form display, redirect or AJAX here
}



function handleOption(option) {
  const chatBody = document.getElementById("chat-body");

  // Show the user’s selection
  const userMsg = document.createElement("div");
  userMsg.className = "chat-msg user-msg";
  userMsg.innerHTML = `<p><strong>You:</strong> ${option}</p>`;
  chatBody.appendChild(userMsg);

  // Ask for email input
 // Ask for email input with elegant design
  const botMsg = document.createElement("div");
  botMsg.className = "chat-msg bot-msg";
  botMsg.innerHTML = `
    <div style="
      background: #f8f9fa;
      border-radius: 12px;
      padding: 15px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
      margin-top: 10px;
    ">
      <p style="margin-bottom: 8px; font-weight: 500; color: #333;">Please enter your email to continue:</p>
      <input type="email" id="user-email" placeholder="you@example.com"
        style="
          width: 100%;
          padding: 10px 12px;
          font-size: 14px;
          border: 1px solid #ccc;
          border-radius: 8px;
          outline: none;
          margin-bottom: 10px;
          box-sizing: border-box;
        ">
      <button onclick="submitEmail('${option}')" style="
        background-color: #6c5ce7;
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.3s ease;
      " onmouseover="this.style.backgroundColor='#5a4bdc'" onmouseout="this.style.backgroundColor='#6c5ce7'">Send</button>
    </div>
  `;
  chatBody.appendChild(botMsg);
    // Auto-scroll to bottom
  chatBody.scrollTop = chatBody.scrollHeight;
}

function submitEmail(option) {
  const emailInput = document.getElementById("user-email");
  const email = emailInput.value.trim();

  if (!email || !email.includes("@")) {
    alert("Please enter a valid email address.");
    return;
  }

  const chatBody = document.getElementById("chat-body");

  // Show user's entered email
  const userEmailMsg = document.createElement("div");
  userEmailMsg.className = "chat-msg user-msg";
  userEmailMsg.innerHTML = `<p><strong>Email Submitted:</strong> ${email}</p>`;
  chatBody.appendChild(userEmailMsg);

  // Send email + query to backend
  fetch("/HomeDen/save-chat-query/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      query: option,
    }),
  })
  .then(response => response.json())
  .then(data => {
    const confirmMsg = document.createElement("div");
    confirmMsg.className = "chat-msg bot-msg";

    if (data.status === "success") {
      confirmMsg.innerHTML = `<p>✅ Thanks! We've received your "<strong>${option}</strong>" request. Our team will contact you at <strong>${email}</strong>.</p>`;
    } else {
      confirmMsg.innerHTML = `<p>⚠️ Oops! Something went wrong. Please try again later.</p>`;
    }

    chatBody.appendChild(confirmMsg);
  })
  .catch(error => {
    console.error("Error:", error);

    const errorMsg = document.createElement("div");
    errorMsg.className = "chat-msg bot-msg";
    errorMsg.innerHTML = `<p>❌ Failed to send your request. Please try again later.</p>`;
    chatBody.appendChild(errorMsg);
  });
}


