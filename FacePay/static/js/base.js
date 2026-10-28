let menu = document.querySelector("#menu-bars");
let navbar = document.querySelector(".navbar");
menu.onclick = () => {
  menu.classList.toggle("fa-times");
  navbar.classList.toggle("active");
};
let section = document.querySelectorAll("section");
let navLinks = document.querySelectorAll("header .navbar a");

window.onscroll = () => {
  menu.classList.remove("fa-times");
  navbar.classList.remove("active");
  section.forEach((sec) => {
    let top = window.scrollY;
    let height = sec.offsetHeight;
    let offset = sec.offsetTop - 150;
    let id = sec.getAttribute("id");
    if (top >= offset && top < offset + height) {
      navLinks.forEach((links) => {
        links.classList.remove("active");
        document
          .querySelector("header .navbar a[href*=" + id + "]")
          .classList.add("active");
      });
    }
  });
};

document.querySelector("#cart-icon").onclick = () => {
  document.querySelector("#cart-form").classList.toggle("active");
};
document.querySelector("#close-cart").onclick = () => {
  document.querySelector("#cart-form").classList.remove("active");
};

document.querySelector("#close-alert").onclick = () => {
  document.querySelector("#popup-alert-form").classList.remove("active");
};


// document.querySelector("#pay-submit-btn").onclick = () => {
//   document.querySelector("#cart-form").classList.remove("active");
//   document.querySelector("#checkout-form").classList.toggle("active");
//   document.getElementById("video_feed").src = '{{url_for("views.video_feed")}}'
// };
// document.querySelector("#close-checkout").onclick = () => {
//   document.querySelector("#checkout-form").classList.remove("active");
// };

const addtoCartButton = document.querySelectorAll("#add-to-cart");
// console.log(addtoCartButton)

addtoCartButton.forEach(function (button, index) {
  button.addEventListener("click", function (event) {
    {
      var btnItem = event.target;
      var product = btnItem.parentElement.parentElement.parentElement;
      var productImg = product.querySelector("img").src;
      var productName = product.querySelector("h2").innerText;
      var productPrice = product.querySelector(".card__price .money").innerText;
      addCart(productPrice, productImg, productName);
    }
  });
});

function addCart(productPrice, productImg, productName) {
  var addtr = document.createElement("tr");
  var cartItem = document.querySelectorAll(".tbody-cart tr");
  for (var i = 0; i < cartItem.length; i++) {
    var productT = document.querySelectorAll(".productName");

    if (productT[i].innerHTML == productName) {
      document.getElementById("setImgDemo").src = productImg;

      var nameProductX = document.querySelector(".success__name");
      nameProductX.innerHTML = productName.toLocaleString("de-DE");

      var priceProductX = document.querySelector(".success__price span");
      priceProductX.innerHTML = productPrice.toLocaleString("de-DE");

      var inputCounterXX = document.querySelectorAll("input");
      var productCount = document.querySelector("#show-product-in-cart");
      productCount.innerHTML = inputCounterXX[i].value.toLocaleString("de-DE");

      document.querySelector("#popup-alert-form").classList.toggle("active");
      // alert("Sản phẩm đã có trong giỏ hàng !")
      document.querySelector("#add-more-product").onclick = () => {
        var inputCounterX = document.querySelectorAll("input");
        inputCounterX[i].value++;
        document.querySelector("#popup-alert-form").classList.remove("active");
        cartTotal();
      };
      document.querySelector("#review-cart").onclick = () => {
        document.querySelector("#popup-alert-form").classList.remove("active");
        document.querySelector("#cart-form").classList.toggle("active");
      };
      document.querySelector("#close-cart").onclick = () => {
        document.querySelector("#cart-form").classList.remove("active");
      };
      return;
    }
  }
  // var trcontent = '<tr id="tr-cart-id"><td><div class="table-p__box"><div class="table-p__img-wrap"><img class="u-img-fluid" src="'+productImg+'" alt=""></div><div class="table-p__info"><span class="table-p__name"><a href="#" class="productName">'+productName+'</a></span><span class="table-p__category"><a href="#">Sport</a></span><ul class="table-p__variant-list"><li><span>Size: 22</span></li><li><span>Color: Red</span></li></ul></div></div></td><td><p class="table-p__price"><span class="money">'+productPrice+'</span><sup>đ</sup></p></td><td><div class="table-p__input-counter-wrap"><div class="input-counter"><span id="inputminus" class="input-counter__minus fas fa-minus"></span><input id="input-counter-id" class="input-counter__text input-counter--text-primary-style" type="text" value="1" data-min="1" data-max="1000"><span id="inputplus" class="input-counter__plus fas fa-plus"></span></div></div></td><td><div class="table-p__del-wrap"><a class="far fa-trash-alt table-p__delete-link"></a></div></td></tr>'
  var trcontent =
    '<tr id="tr-cart-id"><td><div class="table-p__box"><div class="table-p__img-wrap"><img class="u-img-fluid" src="' +
    productImg +
    '" alt=""></div><div class="table-p__info"><span class="table-p__name"><a href="#" class="productName">' +
    productName +
    '</a></span><span class="table-p__category"><a href="#">Sport</a></span><ul class="table-p__variant-list"><li><span>Size: 22</span></li><li><span>Color: Red</span></li></ul></div></div></td><td><p class="table-p__price"><span class="money">' +
    productPrice +
    '</span><sup>đ</sup></p></td><td><div class="table-p__input-counter-wrap"><div class="input-counter"><span id="decrement" onclick="stepper(this)" class="input-counter__minus fas fa-minus"></span><input id="input-counter-id" class="input-counter__text input-counter--text-primary-style" type="text" value="1" id="my-input"><span id="increment" onclick="stepper(this)" class="input-counter__plus fas fa-plus"></span></div></div></td><td><div class="table-p__del-wrap"><a class="far fa-trash-alt table-p__delete-link"></a></div></td></tr>';
  addtr.innerHTML = trcontent;
  var cartTable = document.querySelector(".tbody-cart");
  cartTable.append(addtr);
  Checkout();
  cartTotal();
  deleteCart();
  ItemCounter();
}

function cartTotal() {
  var cartItem = document.querySelectorAll(".tbody-cart tr");
  finalPrice = 0;
  for (var i = 0; i < cartItem.length; i++) {
    var inputValue = cartItem[i].querySelector("input").value;
    var productPrice = cartItem[i].querySelector(".money").innerHTML.split(".")
    if (productPrice.length == 2){
      productPriceX = productPrice[0]+productPrice[1]
    }else{
      productPriceX = productPrice[0]+productPrice[1]+productPrice[2]
    }
    totalPrice = inputValue * productPriceX
    finalPrice += totalPrice;
  }
  var finalPriceA = document.querySelector(".total-price");
  finalPriceA.innerHTML = finalPrice.toLocaleString("de-DE");

  var data = document.querySelectorAll(".tbody-cart tr")
  DataJSON = []
  for (var i=0;i<data.length;i++){
    var jsonData = {};
    var url_img = data[i].querySelector("img").src
    var name = data[i].querySelector(".productName").innerText;
    var price = data[i].querySelector(".money").innerText;
    var quantity = data[i].querySelector("input").value;
    // console.log(quantity)
    jsonData.url_img = url_img
    jsonData.name = name
    jsonData.price = price
    jsonData.quantity = quantity
    DataJSON[i] = jsonData
  }
  // xxxx = JSON.stringify(DataJSON)
  document.getElementById("data-purchase").value = JSON.stringify(DataJSON)
  document.getElementById("purchase").value = finalPrice
  
  // console.log(JSON.parse(xxxx)[0])

  inputChange();
  Checkout();
}

function Checkout(){
  var cartItemCounter = document.querySelectorAll(".tbody-cart tr");
  if(cartItemCounter.length == 0 ) {
    document.getElementById("pay-submit-btn").value ="GIỎ HÀNG TRỐNG!"
    document.getElementById("pay-submit-btn").type ="button"
  }
  else{
    document.getElementById("pay-submit-btn").value ="THANH TOÁN"
    document.getElementById("pay-submit-btn").type ="submit"
  }
}
Checkout();

function deleteCart() {
  var cartItem = document.querySelectorAll(".tbody-cart tr");
  for (var i = 0; i < cartItem.length; i++) {
    var productT = document.querySelectorAll(".table-p__del-wrap");
    productT[i].addEventListener("click", function (event) {
      var cartDelete = event.target;
      var cartItemDelete = cartDelete.parentElement.parentElement.parentElement;
      cartItemDelete.remove();
      cartTotal();
      ItemCounter();
    });
  }
}

function inputChange() {
  var cartItem = document.querySelectorAll(".tbody-cart tr");
  for (var i = 0; i < cartItem.length; i++) {
    var inputValue = cartItem[i].querySelector("input");
    inputValue.addEventListener("change", function () {
      cartTotal();
    });
  }
  return inputValue;
}

const deleteAllbtn = document.querySelectorAll("#deleteAllCart");
deleteAllbtn.forEach(function (button, index) {
  button.addEventListener("click", function (event) {
    {
      var cartItem = document.querySelectorAll(".tbody-cart tr");
      for (var i = 0; i < cartItem.length; i++) {
        cartItem[i].remove();
      }
      ItemCounter();
      cartTotal();
    }
  });
});

function ItemCounter() {
  var cartItem = document.querySelectorAll(".tbody-cart tr");
  var finalCounterItem = document.querySelector(".total-item-round");
  finalCounterItem.innerHTML = cartItem.length.toLocaleString("de-DE");
  inputChange();
}

function stepper(btn) {
  let id = btn.getAttribute("id");
  if (id == "increment") {
    btn.parentElement.querySelector("input").value++;
  } else {
    if (btn.parentElement.querySelector("input").value > 1) {
      btn.parentElement.querySelector("input").value--;
    }
  }
  cartTotal();
}

function redirect_to_logout_page() {
  location.replace("/logout")
}
function redirect_to_home_page() {
  location.replace("/")
}
function redirect_to_signup_page() {
  location.replace("/sign_up")
}
function redirect_to_login_page() {
  location.replace("/sign_in")
}
function redirect_to_account_page() {
  location.replace("/account")
}

