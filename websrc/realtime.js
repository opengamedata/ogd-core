
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
  var bar = document.querySelector('.leftbar');
  var dash = document.querySelector('.rightdash');
  // ADD SELECT GAME OPTION
  var select = document.createElement("SELECT");
  select.id = "mySelect";
  document.getElementById("dropdown_area").appendChild(select);
  generate_options(['CRYSTAL', 'WAVES', 'LAKELAND', 'JOWILDER'])
  sess_list = new SessionList();
  window.setInterval(() => {
    try {
      sess_list.refreshActiveSessions();
      if (sess_list.selected_session_id != -1)
      {
        sess_list.refreshDisplayedSession();
      }
    }
    catch(err) {
      console.log(err.message);
      throw err;
    }
  }, 5000);
}

// Simple set minus operation, based on a suggestion on StackOverflow.
// just filter A based on B not having the element.
function setMinus(A, B) {
  return new Set([...A].filter(x => !B.has(x)));
}

class SessionList
{
  constructor() {
    this.active_game = document.getElementById("mySelect").value;
    this.active_session_ids = [];
    this.displayed_session_ids = [];
    this.selected_session_id = -1;
    this.refreshActiveSessionList();
  }

  refreshActiveSessionList() {
    let that = this;
    function active_sessions_handler(result) {
      that.active_session_ids = JSON.parse(result);
      console.log(`Refreshed session IDs: ${that.active_session_ids}`);
      that.refreshSessionDisplayList();
    };
    Server.get_all_active_sessions(active_sessions_handler, this.active_game);
  }

  refreshSessionDisplayList() {
    let that = this;
    let display_set = new Set(this.displayed_session_ids);
    let active_set = new Set(this.active_session_ids);
    let remove_set = setMinus(display_set, active_set); // subtract active from display to get inactives.
    let add_set    = setMinus(active_set, display_set); // subtract display from active to get new sessions.
    let session_list_area = document.getElementById("session_list");
    if (remove_set.size > 0) {
      let child_nodes = Array.from(session_list_area.children);
      for (let session_link_id in child_nodes) {
        let session_link = child_nodes[session_link_id];
        if (remove_set.has(session_link.id)) {
          session_link.remove();
          if (this.selected_session_id == session_link.id) { this.clearSelected(); }
        }
      }
    }
    for (let id of add_set) {
      let session_id = id;
      let session_div = document.createElement("div");
      session_div.id = session_id;
      let session_link = document.createElement("a");
      session_link.onclick = function() { that.displaySelectedSession(session_id); }
      session_link.innerText = session_id;
      session_link.href = `#${session_id}`;
      session_div.appendChild(session_link);
      session_div.appendChild(document.createElement("br"));
      session_list_area.appendChild(session_div);
    }
    this.displayed_session_ids = [...this.active_session_ids]; // at this point, these should be the same.
  }

  displaySelectedSession(session_id) {
    let that = this;
    this.selected_session_id = session_id;
    let display_area = document.getElementById("prediction_display_area");
    display_area.innerText = session_id;
    let predictions_handler = function(result) {
      console.log(`Got back predictions: ${result}`);
      let predictions_raw = JSON.parse(result);
      let prediction_list = predictions_raw[that.selected_session_id]
      for (let prediction_name in prediction_list) {
        let prediction_value = prediction_list[prediction_name];
        let next_prediction = document.createElement("div");
        next_prediction.id=prediction_name;
        let title = document.createElement("h3");
        title.innerText = prediction_name;
        next_prediction.appendChild(title);
        let value = document.createElement("div");
        value.id = `${prediction_name}_val`;
        value.innerText = prediction_value;
        next_prediction.appendChild(value);
        next_prediction.appendChild(document.createElement("br"));
        display_area.appendChild(next_prediction);
      }
    };
    Server.get_predictions_by_sessID(predictions_handler, session_id, that.active_game);
  }

  refreshDisplayedSession()
  {
    console.log("Starting to refresh displayed session");
    let that = this;
    let predictions_handler = function(result) {
      console.log(`Got back predictions: ${result}`);
      let predictions_raw = JSON.parse(result);
      let prediction_list = predictions_raw[that.selected_session_id]
      for (let prediction_name in prediction_list) {
        let prediction_value = prediction_list[prediction_name];
        let value = document.getElementById(`${prediction_name}_val`);
        value.innerText = prediction_value;
      }
    };
    Server.get_predictions_by_sessID(predictions_handler, session_id, that.active_game);
  }

  clearSelected() {
    // here we'll just clear the stuff displayed in the prediction area.
    let prediction_display_area = document.getElementById("prediction_display_area");
    prediction_display_area.innerText = '';
    while (prediction_display_area.firstChild > 0) {
      prediction_display_area.removeChild(prediction_display_area.firstChild);
    }
    this.selected_session_id = -1;
  }
}