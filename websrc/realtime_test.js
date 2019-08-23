toydata = {
  "Wisconsin": {
    "Milwaukee": {
      "1435": {
        "SessionID": "1435",
        "Time": "10:92",
        "Event Category": "Buy",
        "Event Complex": "slbkfn;ks;fjb;kfsnjdslnsbedbs",
      },
      "1436": {},
      "1437": {},
      "1438": {},
      "1439": {},
      "1434": {},
      "1433": {},
      "1432": {},
      "1431": {},
      "1430": {},
      "1440": {},
      "1450": {},
    },
    "Madison": {
      "1275": {}
    },
    "Delafield": {
      "12": {}
    },
    "Oconomowoc": {
      "1214": {}
    }
  },
  "Alabama": {},
  "Kansas": {},
  "Utah": {}
};

active_sessions = {};
cur_game_id = 'CRYSTAL'




var statebar = document.querySelector('.statebar');
statebar.innerHTML = '';
var citybar = document.querySelector('.citybar');
var screens = document.querySelector('.screens');
var tablediv = document.querySelector('.table');
var table = document.createElement('table');
tablediv.appendChild(table);
// ADD SELECT GAME OPTION
var select = document.createElement("SELECT");
select.id = "mySelect";
statebar.appendChild(select);
generate_options(['CRYSTAL', 'WAVES', 'LAKELAND', 'JOWILDER'])

function change_games(game_id){
  cur_game_id = game_id;
  statebar.innerHTML = '';
  statebar.appendChild(select);
  citybar.innerHTML = '';
  active_sessions = {};
  Server.get_all_active_sessions(function(return_value){
    active_sessions = parse_server_ret_val(return_value)
    console.log({active_sessions: active_sessions})
    for (let state in active_sessions){
      if(Object.keys(active_sessions[state]).length) {
        let a = document.createElement('a');
        let linkText = document.createTextNode(state);
        a.appendChild(linkText);
        a.title = state;
        a.href = '#';
        a.onclick = function(evt){
          listcities(state)
          document.querySelectorAll('.statebar a').forEach(function(x){x.style.backgroundColor = 'initial';});
          a.style.backgroundColor = 'teal'
          return false;
        }
        statebar.appendChild(a);
      }
    }
  }, cur_game_id);
}

function getGreeting()
{
  console.log("In realtime.js, we got a call to getGreeting");
  // Server.getGreeting(function callback(result) {document.getElementByID("greeting-drop").innerHTML = result.toString();});
  Server.get_feature_names_by_game(
    function callback(result) {document.getElementById("greeting-drop").innerHTML = result.toString();},
    "CRYSTAL"
  );
}

function listcities(state){
  citybar.innerHTML = '';
  for(let city in active_sessions[state]) if (Object.keys(active_sessions[state][city]).length){
    let a = document.createElement('a');
    let linkText = document.createTextNode(city);
    a.appendChild(linkText);
    a.title = city;
    a.href = '#';
    a.onclick = function(evt){
      showplayers(state, city)
      document.querySelectorAll('.citybar a').forEach(function(x){x.style.backgroundColor = 'initial';});
      a.style.backgroundColor = 'teal'
      return false;
    }
    citybar.appendChild(a);
  }
}

function showplayers(state, city){
  screens.innerHTML = '';
  table.innerHTML = '';
  console.log(active_sessions[state][city]);
  player_sessIDs = active_sessions[state][city];
  Server.get_prediction_names_by_game(function(return_value){
    headers = parse_server_ret_val(return_value)["stub:prediction_names"]
    headers.unshift('SessID')
    generateTableHead(table, headers);
    generateTable(table, player_sessIDs, headers);
  }
    ,cur_game_id)
  for(let playerid in player_sessIDs){
    create_canvas();
  }
}

function create_canvas(){
  canvas = document.createElement("canvas");
  canvas.style.border = '1px solid red'
  canvas.width = screens.clientWidth / 3 - 2
  canvas.height = canvas.width*3/4;
  screens.appendChild(canvas);
  var ctx = canvas.getContext("2d");
  ctx.fillStyle = "black";
  ctx.fillRect(0,0,100,100);
}

function generateTableHead(table, headers) {
  let thead = table.createTHead();
  let row = thead.insertRow();
  for (let head of headers) {
    let th = document.createElement("th");
    let text = document.createTextNode(head);
    th.appendChild(text);
    row.appendChild(th);
  }
}
function generateTable(table, player_sessIDs, headers) {
  for (let sessID of player_sessIDs) {
    Server.get_predictions_by_sessID(function(return_value){
      predictions = parse_server_ret_val(return_value);
      let row = table.insertRow();
      sessID = Object.keys(predictions)[0]
      predictions = predictions[sessID]
      predictions['SessID'] = sessID
      for (prediction_name of headers) {
        let cell = row.insertCell();
        var text = null;
        text = document.createTextNode(predictions[prediction_name]);
        cell.appendChild(text);
      }
    },sessID, cur_game_id);
  }
}

function generate_options(option_texts){
  select = document.getElementById("mySelect");
  select.onchange = function(){if (this.value) change_games(this.value);};
  for(txt of option_texts){
    var option = document.createElement("option");
    option.text = txt;
    select.add(option);
  }
}
// var headers = {
//   "SessionID": "SessionID",
//   "Time": "Time",
//   "Event Category": "Event Category",
//   "Event Complex": "Event Complex",
// };

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

change_games('CRYSTAL');

