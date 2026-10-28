let circularProgress = document.querySelector(".circular-progress"),
    progressValue = document.querySelector(".progress-value");

let progressStartValue = -30,    
    progressEndValue = 100,    
    speed = 50;
    
let progress = setInterval(() => {
    progressStartValue++;
    circularProgress.style.background = `conic-gradient(#2ae837 ${progressStartValue * 3.6}deg, #ededed 0deg)`
    if(progressStartValue == progressEndValue){
        clearInterval(progress);
        location.replace("/")
    }    
}, speed);