$('.mail-choice').change(function() {
    if($(this).is(":checked")) {
        $(this).parent().addClass('selected-bg');
  } else {
    $(this).parent().removeClass('selected-bg');
  }
});

const colorInput = document.getElementById("colorpicker");

// colorInput.addEventListener("input", (e) => {
//  document.body.style.setProperty("--button-color", e.target.value);
// });

$('.inbox-calendar').click(function(){
  $('.calendar-container').toggleClass('calendar-show');
 $('.inbox-container').toggleClass('hide');
 $('.mail-detail').toggleClass('hide'); 
});

function redirect_to_home_page() {
  location.replace("/")
}

var x = document.querySelectorAll(".covert-json")
console.log(x[0].value)
for (var i =0;i<x.length;i++){
  y = JSON.parse(x[i].value)
  for (var z=0 ; z<y.length;z++)
  {
    var addtr = document.createElement("tr");
    console.log(y[z])
    product_url_image = y[z].url_img
    product_name = y[z].name
    product_price = y[z].price
    product_quantity = y[z].quantity
    console.log(product_url_image,product_name,product_price,product_quantity)

    var trcontent = '<tr><ul><img style="width: 70px;" src="'+product_url_image+
    '" alt="" ></ul><ul>Tên Sản Phẩm: '+product_name+'-----Giá: '+product_price+'-----Số lượng: '+product_quantity+'</ul></tr>'

    addtr.innerHTML = trcontent;
    var cartTable = document.querySelectorAll("tbody");
    cartTable[i].append(addtr);

    // var trContent ='<!-- <tr> <td class="sm:p-3 py-2 px-1 border-b border-gray-200 dark:border-gray-800"> <div class="flex items-center"> <svg viewBox="0 0 24 24" class="w-4 mr-5 text-yellow-500" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"> <circle cx="12" cy="12" r="10"></circle> <line x1="12" y1="8" x2="12" y2="12"></line> <line x1="12" y1="16" x2="12.01" y2="16"></line> </svg> FacePay </div> </td> <td class="sm:p-3 py-2 px-1 border-b border-gray-200 dark:border-gray-800"> <div class="flex items-center"> <img src="'+product_url_image+'" class="w-12 mr-4" /> </div> </td> <td class="sm:p-3 py-2 px-1 border-b border-gray-200 dark:border-gray-800 md:table-cell hidden">'+product_name+'</td> <td class="sm:p-3 py-2 px-1 border-b border-gray-200 dark:border-gray-800 md:table-cell hidden">'+product_quantity+'</td> <td class="sm:p-3 py-2 px-1 border-b border-gray-200 dark:border-gray-800 text-red-500">'+product_price+'<sup>đ</sup></td> <td class="sm:p-3 py-2 px-1 border-b border-gray-200 dark:border-gray-800"> <div class="flex items-center"> <div class="sm:flex hidden flex-col"> 24.12.2020 <div class="text-gray-400 text-xs">11:16 AM</div> </div> <button class="w-8 h-8 inline-flex items-center justify-center text-gray-400 ml-auto"> <svg viewBox="0 0 24 24" class="w-5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"> <circle cx="12" cy="12" r="1"></circle> <circle cx="19" cy="12" r="1"></circle> <circle cx="5" cy="12" r="1"></circle> </svg> </button> </div> </td> </tr> -->'
    // var cartTable = document.querySelectorAll("tbody");
    // cartTable[i].append(addtr);
  }
}