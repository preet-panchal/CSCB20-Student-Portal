
window.onscroll = function() {myFunction()};

	var navbar = document.getElementById("navbar");
	var sticky = navbar.offsetTop;

	function myFunction() {
  		if (window.pageYOffset >= sticky) {
    		navbar.classList.add("sticky")
  		} else {
    		navbar.classList.remove("sticky");
  		}
	}

	

var total = document.getElementsByClassName("announcement");
var i;

for (i = 0; i < total.length; i++) {
	total[i].addEventListener("click", function() {
		this.classList.toggle("active");
		var panel = this.nextElementSibling;
		if (panel.style.display === "block") {
			 panel.style.display = "none";
		} else {
			panel.style.display = "block";
		}
	});
}

