const buttons = document.querySelectorAll(".authPopup");
const container = document.querySelector(".authContent");
function handleButtonClick(e) {
    buttons.forEach(btn => {
        btn.style.pointerEvents = "all";
    });

    e.preventDefault();
    const btn = e.currentTarget;
    const btnRect = btn.getBoundingClientRect();
    container.style.transition = 'none';
    container.style.left = `${btnRect.left + btnRect.width / 2}px`;
    container.style.top = `${btnRect.top + btnRect.height / 2}px`;
    container.style.opacity = '0';
    container.style.transform = 'translate(-50%, -50%) scale(0.2)';
    container.parentElement.style.pointerEvents = "none";

    const targetX = window.innerWidth / 2;
    const targetY = window.innerHeight / 2;

    container.style.transition = 'all 500ms ease-out';
    container.style.left = `${targetX}px`;
    container.style.top = `${targetY}px`;
    container.style.opacity = '1';
    container.style.transform = 'translate(-50%, -50%) scale(1)';
    container.style.pointerEvents = "all";
}

buttons.forEach(btn => {
    btn.addEventListener("click", handleButtonClick);
});
const closeAuthContent = () =>{
    container.style.transition='all 600ms ease-out';
    requestAnimationFrame(() => {
        container.style.opacity ='0';
        container.style.transform = 'translate(-50%, -50%) scale(0)';
        console.log(buttons);
        buttons.forEach(btn => {btn.style.pointerEvents="all"});
        document.querySelector('main').style.pointerEvents = 'all';
    });
}
const closeBtn = document.querySelector("#closeBtn");
closeBtn.addEventListener("click", () => {
    closeAuthContent();
});

const switchBtn = document.querySelector('.switch');
switchBtn.addEventListener("click", (e) => {
    if (switchBtn.dataset.type==="signup"){
        e.preventDefault();
        document.querySelector(".modal-content .head .title").innerText="Welcome Back";
        document.querySelector(".switchText").innerText="Don't have an account ?  "
        switchBtn.innerText = "Sign up";
        switchBtn.dataset.type="login";
    }
    else if (switchBtn.dataset.type="login"){
        const html = `Already have an account ?&nbsp; <a href="#" data-type="signup" id="switch">Log in</a>`;
        e.preventDefault();
        document.querySelector(".modal-content .head .title").innerText="Create an Account";
        document.querySelector(".switchText").innerText="Already have an account ?  ";
        switchBtn.innerText = "Log in";
        switchBtn.dataset.type="signup";
    }
});


document.getElementById("logout").addEventListener("click", async () => {
    const res = await fetch("http://localhost:5000/logout", {
        method: "POST",
        credentials: "include"
    });

    const data = await res.json();
    if (data.success) {
        document.querySelector(".sidebar").classList.add("hidden")
        document.querySelector("main").classList.add("full-screen")
        document.querySelector(".auth").style.display="flex"
        // document.querySelector(".get-started").classList.add("authPopup")
        document.querySelector(".get-started").addEventListener("click", handleButtonClick);
        document.querySelector(".authProfile").style.display="none";
        // window.location.reload();
    }
});

// Open/close card when top-right profile picture is clicked
function toggleCard() {
    const card = document.querySelector(".authProfile .card");
    if (card.style.display === "none" || card.style.display === "") {
        card.style.display = "grid";
    } else {
        card.style.display = "none";
    }
}
