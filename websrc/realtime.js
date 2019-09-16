/**
 * Function to initialize data and refresh loop when the page loads.
 */
function onload()
{
  // Set up UI regions.
  var bar = document.querySelector('.leftbar');
  var dash = document.querySelector('.rightdash');
  // Set up the game selection dropdown.
  var select = document.createElement("SELECT");
  select.id = "mySelect";
  document.getElementById("dropdown_area").appendChild(select);
  generate_options(['CRYSTAL', 'WAVES', 'LAKELAND', 'JOWILDER'])
  // Create a SessionList instance for tracking state, and start the refresh loop.
  sess_list = new SessionList();
  window.setInterval(() => {
    try {
      sess_list.refreshSessionDisplayList();
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

/** Simple function to generate the list of options for games to view.
 *  Given a list of game names, this populates the 'select' dropdown.
 *  Game switching is handled in a handler function.
 *  @param {*} option_texts A list of game names for the dropdown.
 */
function generate_options(option_texts){
  select = document.getElementById("mySelect");
  let that = this; // the old this-that js hack.
  select.onchange = function(){if (this.value) change_games(sess_list, this.value);};
  for(let txt of option_texts){
    var option = document.createElement("option");
    option.text = txt;
    select.add(option);
  }
}

/**
 * Handler function to change the game whose sessions are on display.
 * Fairly simple, just set the active game and refresh the displayed
 * data
 * @param {} list The SessionList instance for tracking the game and its sessions.
 * @param {*} game_name The name of the game to switch to.
 */
function change_games(list, game_name){
  list.active_game = game_name;
  list.refreshActiveSessionList();
  // TODO: it may be that I should clear the selected session ID.
  //       will check on this later.
}

/**
 * Simple set minus operation, based on a suggestion on StackOverflow.
 * just filter A based on B not having the element.
 * @param {*} A Set from which to subtract another set.
 * @param {*} B Set to subtract from A.
 */
function setMinus(A, B) {
  return new Set([...A].filter(x => !B.has(x)));
}

/**
 * Class to manage data related to sessions for each game.
 * This is responsible for maintaining a list of sessions,
 * as well as displaying the data in the view.
 * Technically, if this were a more complicated page,
 * we might want to split out the data from the display,
 * but this works well for what it is.
 */
class SessionList
{
  /**
   * Constructor for the SessionList class
   * Sets up variables to track the active game, lists of sessions ids
   * (one list is what's active, the other is what's actively displayed),
   * and a selected ID (for detailed display).
   */
  constructor() {
    this.active_game = document.getElementById("mySelect").value;
    this.active_session_ids = [];
    this.displayed_session_ids = [];
    this.selected_session_id = -1;
    this.refreshActiveSessionList();
  }

  /**
   * Function to retrieve a list of currently active sessions.
   * First, we call the CGI backend to get the list. 
   * In the handler, the returned list updates the SessionList data,
   * and then makes a further call to refresh the display list.
   */
  refreshActiveSessionList() {
    let that = this;
    function active_sessions_handler(result) {
      that.active_session_ids = JSON.parse(result);
      console.log(`Refreshed session IDs: ${that.active_session_ids}`);
      that.refreshSessionDisplayList();
    };
    Server.get_all_active_sessions(active_sessions_handler, this.active_game);
  }

  /**
   * Function to update the list of displayed session IDs.
   * This is done in a way that preserves the order of session IDs 
   * as much as possible.
   */
  refreshSessionDisplayList() {
    let that = this;
    let display_set = new Set(this.displayed_session_ids);
    let active_set = new Set(this.active_session_ids);
    let remove_set = setMinus(display_set, active_set); // subtract active from display to get inactives, which are currently displayed.
    let add_set    = setMinus(active_set, display_set); // subtract display from active to get new sessions, which were not displayed yet.
    let session_list_area = document.getElementById("session_list");
    // If there is anything to remove, loop over all sessions in the list. When we find an inactive one, remove it.
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
    // loop over all newly active sessions, adding them to the list.
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
    this.displayed_session_ids = [...this.active_session_ids]; // at this point, these should theoretically be the same.
  }

  /**
   * Function to set up display of predictions for a given session.
   * Once this has been run, another function can be used to update
   * the prediction values in place (without removing and replacing elements).
   * @param {*} session_id The id of the session to display.
   */
  displaySelectedSession(session_id) {
    let that = this;
    this.selected_session_id = session_id;
    let display_area = document.getElementById("prediction_display_area");
    display_area.innerText = `Session ID: ${session_id}`;
    let predictions_handler = function(result) {
      let predictions_raw = JSON.parse(result);
      let prediction_list = predictions_raw[that.selected_session_id]
      // loop over all predictions, adding to the UI.
      for (let prediction_name in prediction_list) {
        let prediction_value = prediction_list[prediction_name];
        // first, make a div for everything to sit in.
        let next_prediction = document.createElement("div");
        next_prediction.id=prediction_name;
        next_prediction.className="resultbox";
        // then, add an element with prediction title to the div
        let title = document.createElement("h3");
        title.innerText = prediction_name;
        next_prediction.appendChild(title);
        // finally, add an element for the prediction value to the div.
        let value = document.createElement("span");
        value.id = `${prediction_name}_val`;
        value.innerText = prediction_value;
        next_prediction.appendChild(value);
        next_prediction.appendChild(document.createElement("br"))
        display_area.appendChild(next_prediction);
      }
    };
    Server.get_predictions_by_sessID(predictions_handler, session_id, that.active_game);
  }

  /**
   * Function to update the prediction values for a displayed session.
   * This assumes a session has been selected, and its id stored in
   * the SessionList selected_session_id variable.
   */
  refreshDisplayedSession()
  {
    let that = this;
    let predictions_handler = function(result) {
      // console.log(`Got back predictions: ${result}`);
      let predictions_raw = JSON.parse(result);
      let prediction_list = predictions_raw[that.selected_session_id]
      // After getting the prediction values, loop over whole list,
      // updating values.
      for (let prediction_name in prediction_list) {
        let prediction_value = prediction_list[prediction_name];
        let value = document.getElementById(`${prediction_name}_val`);
        value.innerText = prediction_value;
      }
    };
    Server.get_predictions_by_sessID(predictions_handler, that.selected_session_id, that.active_game);
  }

  /**
   * Simple function to clear out data display for a selected session.
   * This is mostly intended for when switching to a new session or switching
   * to another game entirely.
   */
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