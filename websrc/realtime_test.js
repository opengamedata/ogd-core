// initialize
var statebar = document.querySelector('.statebar');
statebar.innerHTML = '';
var citybar = document.querySelector('.citybar');
var screens = document.querySelector('.screens');
var tablediv = document.querySelector('.table');

// ADD SELECT GAME OPTION
var select = document.createElement("SELECT");
select.id = "mySelect";
statebar.appendChild(select);
all_games = ['CRYSTAL', 'WAVES', 'LAKELAND', 'JOWILDER'];

function parse_server_ret_val(return_value){
  return_value = return_value.trim()
  second_line = return_value.split(/[\r\n]+/)[1]
  try{
    ret = JSON.parse(second_line);
  } catch(e) {
    ret = second_line
  }
  return ret
}

class TableManager
{
  constructor() {
    this.cur_game_id = all_games[0];
    this.active_sessions = {};
    this.generate_options(all_games);
    this.change_games(this.cur_game_id);
    this.table = document.createElement('table');
    this.is_active = false;
    this.active_state = null;
    this.active_city = null;
    tablediv.appendChild(this.table);
  }

  change_games(game_id){
    // reset global UI elements
    statebar.innerHTML = '';
    statebar.appendChild(select);
    citybar.innerHTML = '';
    // reset local table manager elements
    this.cur_game_id = game_id;
    this.active_sessions = {};
    this.is_active = false;
    // then, set up to get sessions.
    var that = this; // stupid javascript hack. 'Cause js is a hack language.
    let handler = function(return_value){
      that.active_sessions = parse_server_ret_val(return_value)
      console.log({active_sessions: that.active_sessions})
      for (let state in that.active_sessions){
        if(Object.keys(that.active_sessions[state]).length) {
          let a = document.createElement('a');
          let linkText = document.createTextNode(state);
          a.appendChild(linkText);
          a.title = state;
          a.href = '#';
          a.onclick = function(evt){
            that.is_active = false;
            that.listcities(state)
            that.active_state = state;
            document.querySelectorAll('.statebar a').forEach(function(x){x.style.backgroundColor = 'initial';});
            a.style.backgroundColor = 'teal'
            return false;
          }
          statebar.appendChild(a);
        }
      }
    };
    // get all the active sessions, and handle.
    Server.get_all_active_sessions(handler, this.cur_game_id);
  }

  getGreeting()
  {
    console.log("In realtime.js, we got a call to getGreeting");
    // Server.getGreeting(function callback(result) {document.getElementByID("greeting-drop").innerHTML = result.toString();});
    Server.get_feature_names_by_game(
      function callback(result) {document.getElementById("greeting-drop").innerHTML = result.toString();},
      "CRYSTAL"
    );
  }

  listcities(state){
    citybar.innerHTML = '';
    for(let city in this.active_sessions[state]) if (Object.keys(this.active_sessions[state][city]).length){
      let that = this; // standard js this-that hack.
      let a = document.createElement('a');
      let linkText = document.createTextNode(city);
      a.appendChild(linkText);
      a.title = city;
      a.href = '#';
      a.onclick = function(evt){
        that.active_city = city;
        that.is_active = true;
        that.showplayers(state, city)
        document.querySelectorAll('.citybar a').forEach(function(x){x.style.backgroundColor = 'initial';});
        a.style.backgroundColor = 'teal'
        return false;
      }
      citybar.appendChild(a);
    }
  }

  showplayers(state, city){
    screens.innerHTML = '';
    this.table.innerHTML = '';
    console.log(`players for ${city}, ${state}: ${this.active_sessions[state][city]}`);
    let player_sessIDs = this.active_sessions[state][city];
    let that = this;
    let handler = function(return_value){
      that.headers = parse_server_ret_val(return_value)["stub:prediction_names"]
      that.headers.unshift('SessID')
      that.generateTableHead();
      that.generateTable(player_sessIDs);
    };
    Server.get_prediction_names_by_game(handler ,this.cur_game_id);
    for(let playerid in player_sessIDs){
      screens.appendChild(this.create_canvas());
    }
  }

  create_canvas(){
    let canvas = document.createElement("canvas");
    canvas.style.border = '1px solid red'
    canvas.width = screens.clientWidth / 3 - 2
    canvas.height = canvas.width*3/4;
    var ctx = canvas.getContext("2d");
    ctx.fillStyle = "black";
    ctx.fillRect(0,0,100,100);
    return canvas;
  }

  generateTableHead() {
    let thead = this.table.createTHead();
    let row = thead.insertRow();
    for (let head of this.headers) {
      let th = document.createElement("th");
      let text = document.createTextNode(head);
      th.appendChild(text);
      row.appendChild(th);
    }
  }

  generateTable(player_sessIDs) {
    let that = this;
    // handler to get predictions put into UI
    let prediction_handler = function(return_value){
      let predictions = parse_server_ret_val(return_value);
      let row = that.table.insertRow();
      let sessID = Object.keys(predictions)[0]
      predictions = predictions[sessID]
      predictions['SessID'] = sessID
      for (let prediction_name of that.headers) {
        let cell = row.insertCell();
        var text = null;
        text = document.createTextNode(predictions[prediction_name]);
        cell.appendChild(text);
      }
    };
    // handler to print features, so we know they ran.
    let features_handler = function(result) {
      console.log("feature results:");
      console.log(result);
    }
    // for each ID, get predictions and features.
    for (let sessID of player_sessIDs) {
      Server.get_predictions_by_sessID(prediction_handler ,sessID, this.cur_game_id);
      Server.get_features_by_sessID(features_handler, sessID, this.cur_game_id);
    }
  }

  generate_options(option_texts){
    select = document.getElementById("mySelect");
    let that = this; // the old this-that js hack.
    select.onchange = function(){if (this.value) that.change_games(this.value);};
    for(let txt of option_texts){
      var option = document.createElement("option");
      option.text = txt;
      select.add(option);
    }
  }

  refresh() {
    let player_sessIDs = this.active_sessions[this.active_state][this.active_city];
    let num = this.table.rows.length;
    // Hacky bit to get the table row to refresh.
    // TODO: fix the hack by updating table with new values, instead of
    // re-generating the rows every update. To do this, we really need to fix up the table construction code, so it tracks where data actually went.
    for (let i = 1; i < num; i++) {
      this.table.deleteRow(1);
    }
    this.generateTable(player_sessIDs);
  }
  // var headers = {
  //   "SessionID": "SessionID",
  //   "Time": "Time",
  //   "Event Category": "Event Category",
  //   "Event Complex": "Event Complex",
  // };

};

tm = new TableManager();
window.setInterval(() => {
  try {
    if (tm.is_active) {
      tm.refresh();
    }
  }
  catch(err) {
    console.log(err.message);
    throw err;
  }
}, 5000);