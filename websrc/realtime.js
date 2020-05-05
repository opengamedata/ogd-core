/**
 * Function to initialize data and refresh loop when the page loads.
 */
function onload()
{
  // Set up UI regions.
  var bar = document.querySelector('.leftbar');
  var dash = document.querySelector('.rightdash');
  // Set up the game selection dropdown.
  generate_options(['CRYSTAL', 'WAVES', 'LAKELAND', 'JOWILDER'])
  // Create a SessionList instance for tracking state, and start the refresh loop.
  sess_list = new SessionList();
  document.getElementById("require_pid").onclick = function() {
      sess_list.require_player_id = this.checked;
  }
  window.setInterval(() => {
    try {
      sess_list.updateActiveSessionList();
      if (sess_list.selected_session_id != -1)
      {
        sess_list.refreshSelectedSession();
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
  select = document.getElementById("select_game");
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
  list.updateActiveSessionList();
  list.clearSelected();
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
    this.active_game = document.getElementById("select_game").value;
    this.active_sessions = [];
    this.active_session_ids = [];
    this.displayed_session_ids = [];
    this.selected_session_id = -1;
    this.require_player_id = document.getElementById("require_pid").checked;
    this.updateActiveSessionList();
  }

  /**
   * Function to retrieve a list of currently active sessions.
   * First, we call the CGI backend to get the list. 
   * In the handler, the returned list updates the SessionList data,
   * and then makes a further call to refresh the display list.
   */
  updateActiveSessionList() {
    let that = this;
    // let start_time = Date.now();
    function active_sessions_handler(result) {
      let parsed_sessions = 'null';
      // console.log(`Got back with active sessions, time taken was: ${(Date.now() - start_time)/1000} seconds.`);
      try
      {
        parsed_sessions = JSON.parse(result);
      }
      catch (err)
      {
        console.log(`Could not parse result as JSON:\n ${result}`);
        return;
      }
      that.active_sessions = parsed_sessions;
      console.log(`Refreshed session IDs: ${that.active_sessions}`);
      that.active_session_ids = Array.from(Object.keys(that.active_sessions));
      that.updateSessionDisplayableList();
    };
    Server.get_all_active_sessions(active_sessions_handler, this.active_game, this.require_player_id);
  }

  /**
   * Function to update the list of displayed session IDs.
   * This is done in a way that preserves the order of session IDs 
   * as much as possible.
   */
  updateSessionDisplayableList() {
    let that = this;
    let display_set = new Set(this.displayed_session_ids);
    let active_set = new Set(this.active_session_ids);
    let remove_set = setMinus(display_set, active_set); // subtract active from display to get inactives, which are currently displayed.
    let add_set    = setMinus(active_set, display_set); // subtract display from active to get new sessions, which were not displayed yet.

    this.refreshDisplayedSessionList(add_set, remove_set)

    this.displayed_session_ids = [...this.active_session_ids]; // at this point, these should theoretically be the same.
  }

  refreshDisplayedSessionList(add_set, remove_set)
  {
    let session_list_area = document.getElementById("session_list");
    // First, refresh what's in the list.
    let child_nodes = Array.from(session_list_area.children);
    for (let session_link_num in child_nodes) {
      let session_link = child_nodes[session_link_num];
      let session_id = session_link.id;
      // let session_link = child_nodes[`div_${session_id}`];
      // A) If object is in remove set, remove it.
      if (remove_set.has(session_id)) {
        session_link.remove();
        if (this.selected_session_id == session_link.id) { this.clearSelected(); }
      }
      // B) Else, update the max and current levels.
      else {
        this.refreshDisplayedSession(session_id);
      }
    }
    // loop over all newly active sessions, adding them to the list.
    for (let id of add_set) {
      let session_id = id;
      let session_div = this.generateDisplayedSession(session_id);
      session_list_area.appendChild(session_div);

      this.refreshDisplayedSession(session_id);
    }
  }

  generateDisplayedSession(session_id)
  {
    let that = this;
    // create a div for everything
    let session_div = document.createElement("div");
    session_div.id = session_id;
    // create a link to select the session
    let session_link = document.createElement("a");
    session_link.onclick = function() { that.generateSelectedSession(session_id); }
    session_link.innerText = session_id;
    session_link.href = `#${session_id}`;
    session_div.appendChild(session_link);
    // create a div to display current level.
    let cur_level_div = document.createElement("div");
    cur_level_div.id = `cur_level_${session_id}`;
    session_div.appendChild(cur_level_div);
    let max_level_div = document.createElement("div");
    max_level_div.id = `max_level_${session_id}`;
    session_div.appendChild(max_level_div);
    let seconds_inactive_div = document.createElement("div");
    seconds_inactive_div.id = `seconds_inactive_${session_id}`;
    session_div.appendChild(seconds_inactive_div);
    session_div.appendChild(document.createElement("br"));

    return session_div;
  }

  refreshDisplayedSession(session_id)
  {
      let cur_level_div = document.getElementById(`cur_level_${session_id}`);
      cur_level_div.innerText = `current: ${this.active_sessions[session_id]["cur_level"].toString()}`;
      let max_level_div = document.getElementById(`max_level_${session_id}`);
      max_level_div.innerText = `max: ${this.active_sessions[session_id]["max_level"].toString()}`;
      let seconds_inactive_div = document.getElementById(`seconds_inactive_${session_id}`);
      seconds_inactive_div.innerText = `seconds inactive: ${this.active_sessions[session_id]["idle_time"].toString()}`;
  }

  /**
   * Function to set up display of predictions for a given session.
   * Once this has been run, another function can be used to update
   * the prediction values in place (without removing and replacing elements).
   * @param {*} session_id The id of the session to display.
   */
  generateSelectedSession(session_id) {
    let that = this;
    this.selected_session_id = session_id;
    let display_area = document.getElementById("prediction_display_area");
    display_area.innerText = `Session ID: ${session_id}`;
    let start_time = Date.now();
    let predictions_handler = function(result) {
      console.log(`Got back with initial predictions, time taken was: ${(Date.now() - start_time)/1000} seconds.`);
      let predictions_raw = 'null';
      try
      {
        predictions_raw = JSON.parse(result);
      }
      catch (err)
      {
        console.log(`Could not parse result as JSON:\n ${result}`);
        return;
      }
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
  refreshSelectedSession()
  {
    let that = this;
    // let start_time = Date.now();
    let predictions_handler = function(result) {
      // console.log(`Got back with updated predictions, time taken was: ${(Date.now() - start_time)/1000} seconds.`);
      // console.log(`Got back predictions: ${result}`);
      let predictions_raw = 'null';
      try
      {
        predictions_raw = JSON.parse(result);
      }
      catch (err)
      {
        console.log(`Could not parse result as JSON:\n ${result}`);
        return;
      }
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