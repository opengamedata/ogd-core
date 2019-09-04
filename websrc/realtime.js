
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
      sess_list.refreshDisplayedSessions();
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
    this.refreshActiveSessions();
    this.refreshDisplayedSessions();
  }

  refreshActiveSessions() {
    let that = this;
    function active_sessions_handler(result) {
      that.active_session_ids = result;
      console.log(`Refreshed session IDs: ${that.active_session_ids}`);
    };
    Server.get_all_active_sessions(active_sessions_handler, this.active_game);
  }

  refreshDisplayedSessions() {
    let that = this;
    let display_set = new Set(this.displayed_session_ids);
    let active_set = new Set(this.active_session_ids);
    let remove_set = setMinus(display_set, active_set); // subtract active from display to get inactives.
    let add_set    = setMinus(active_set, display_set); // subtract display from active to get new sessions.
    let session_list_area = document.getElementById("session_list");
    for (let session_link in session_list_area.children) {
      if (remove_set.has(session_link.id)) {
        session_link.remove();
      }
    }
    for (let id in add_set) {
      let session_link = document.createElement("a");
      let session_id = id;
      session_link.onclick = function() { that.displaySession(session_id); }
      session_link.innerText = session_id;
    }
    this.displayed_session_ids = [...this.active_session_ids]; // at this point, these should be the same.
  }

  displaySession(session_id) {
    document.getElementById("prediction_display_area").innerText = session_id;
  }
}