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
}
//REALTIME API CALL

// realtime_api.get_all_active_sessions(gameID) { //gameID eg 'CRYSTAL'
//   //returns object of form:
//   {
//     "STATE0": {
//       "CITY0": [SessID0, SessID1, SessID2, ... sessIDn],
//       "CITY1": [SessID0...]
//       etc.
//     }
//     "STATE1": {
//       "CITY0": [SessID0, SessID1, SessID2, ... sessIDn],
//       "CITY1": [SessID0...]
//     }
//   }
// }
//   //returns {} if there are no active sessions.
// realtime_api.get_active_sessions_by_loc(gameID, state, city){
//   GameID - str ID of game eg 'CRYSTAL'
//   state - str state name as returned by get_all_active_sessions(GameID)
//   city - str city name as returned by get_all_active_sessions(GameID)
//   returns an array of active sessions eg
//   [SessID0, SessID1, SessID2]
// }
// Note: The _by_sessID functions below are probably going to mostly be run
// in a row, so if its more efficient to input and output whole lists, that
// is fine too.
// realtime_api.get_features_by_sessID(sessID, features=null){
//   returns the features of specific (active) sessID.
//   takes optional argument features which if not null, is an array of feature names
//   specifying which features to return. this would be like:
//   ['GameStart','Fail','GameEnd'].
//   Returns list of features in JSON format
// }
// realtime_api.get_feature_names_by_game(gameID){
//   returns all feature names of that game (any format is fine)
// }
// realtime_api.get_predictions_by_sessID(sessID, predictions=null){
//   returns the predictions of specific (active) sessID.
//   takes optional argument predictions which if not null, is an array of prediction names
//   specifying which predictions to return. this would be like:
//   ['probability to finish lv3' etc.].
//   Returns list of predictions in JSON format
// }
// realtime_api.get_prediction_names_by_game(gameID){
//   returns all prediction names of that game (any format is fine)
// }

/*
Example flow: {
  as of right now, the only game we are thinking of is lakeland, but theoretically the user could choose any game
  populate sidebars/map with data from realtime_api.get_all_active_sessions(gameID)
  user clicks on a state and a city
  optional: user can select subset of features/predictions to display from realtime_api.get_feature/prediction_names_by_game(gameID)
  Every ~5 seconds populate table with subset of features/predictions by {
    loop through sessID in realtime_api.get_active_sessions_by_loc(gameID, state, city)
    set i-th row of the table equal to cells derived from:
      realtime_api.get_predictions_by_sessID(sessID, predictions=subset)
  }



}
*/



var statebar = document.querySelector('.statebar');
statebar.innerHTML = '';
var citybar = document.querySelector('.citybar');
var screens = document.querySelector('.screens');
var tablediv = document.querySelector('.table');

for (let state in toydata){
  if(Object.keys(toydata[state]).length) {
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

function getGreeting()
{
  console.log("Getting greeting...")
  Server.getGreeting(
    function callback(result) {console.log("Reached callback function"); console.log("result was: " + result.toString());  document.getElementById("greeting-drop").innerHTML = result.toString();}
  );
  console.log("...Got back from greeting.")
}

function listcities(state){
  citybar.innerHTML = '';
  for(let city in toydata[state]) if (Object.keys(toydata[state][city]).length){
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
  console.log(toydata[state][city]);
  players = toydata[state][city];
  generateTableHead(table,headers);
  generateTable(table, players, headers)
  for(let playerid in players){
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

function change_tables(value, start=false) {
  let table = document.querySelector("table");
  table.innerHTML = '';
  jQuery.getJSON("http://localhost/GameData%20Site/data/file_list.json",function(result){
    tables = result;
    let table = document.querySelector("table");
    generateTableHead(table, headers);
    generateTable(table, tables[value], headers);
    if(start) generate_options();
  });
}

function generateTableHead(table, headers) {
  let thead = table.createTHead();
  let row = thead.insertRow();
  for (let key in headers) {
    let th = document.createElement("th");
    let text = document.createTextNode(headers[key]);
    th.appendChild(text);
    row.appendChild(th);
  }
}
function generateTable(table, data, headers) {
  for (let setID in data) {
    var set = data[setID]
    let row = table.insertRow();
    for (key in headers) {
      let cell = row.insertCell();
      var text = null;
      switch (key) {
        default:
            text = document.createTextNode(set[key]);
            cell.appendChild(text);

      }
    }
  }
}

function generate_options(){
  select = document.getElementById("mySelect");
  for(table_name in tables){
    var option = document.createElement("option");
    option.text = table_name;
    select.add(option);
  }
}
var headers = {
  "SessionID": "SessionID",
  "Time": "Time",
  "Event Category": "Event Category",
  "Event Complex": "Event Complex",
};
var table = document.createElement('table');
tablediv.appendChild(table);

