var bar = document.querySelector('.leftbar');
var dash = document.querySelector('.rightdash');

function generate_options(option_texts){
  select = document.getElementById("mySelect");
  let that = this; // the old this-that js hack.
  select.onchange = function(){if (this.value) that.change_games(this.value);};
  for(let txt of option_texts){
    var option = document.createElement("option");
    option.text = txt;
    select.add(option);
  }
}

function change_games(){
  
}

// ADD SELECT GAME OPTION
var select = document.createElement("SELECT");
select.id = "mySelect";
bar.appendChild(select);
generate_options(['CRYSTAL', 'WAVES', 'LAKELAND', 'JOWILDER'])