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

function onload()
{
  // ADD SELECT GAME OPTION
  var select = document.createElement("SELECT");
  select.id = "mySelect";
  bar.appendChild(select);
  generate_options(['CRYSTAL', 'WAVES', 'LAKELAND', 'JOWILDER'])
}

class SessionList
{
  constructor()
  {
    this.active_game = document.getElementById("mySelect").value;
    this.session_ids = [];
    let that = this;
    function handler(result) {
      that.session_ids = result;
    };
    Server.get_all_active_sessions(handler, this.active_game);
  }
}