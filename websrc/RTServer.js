class Server
{
   static getGreeting(callback)
   {
      console.log("Received request for greeting")
      var req = new XMLHttpRequest();
      req.onreadystatechange = function()
      {
         if (this.readyState == 4 && this.status == 200)
         {
            console.log("responseText was: " + this.responseText)
            callback(this.responseText.toString());
         }
      }
      req.open("POST", "realtime.cgi", true);
      req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      req.send("method=say_hello");
   }

   //REALTIME API CALL

   static get_all_active_sessions(callback, gameID) //gameID eg 'CRYSTAL'
   {
   //returns object of form:
      // {
      // "STATE0": {
      //    "CITY0": [SessID0, SessID1, SessID2, ... sessIDn],
      //    "CITY1": [SessID0...]
      //    etc.
      // }
      // "STATE1": {
      //    "CITY0": [SessID0, SessID1, SessID2, ... sessIDn],
      //    "CITY1": [SessID0...]
      // }
   }
   //returns {} if there are no active sessions.

   static get_active_sessions_by_loc(callback, gameID, state, city)
   {
   //   GameID - str ID of game eg 'CRYSTAL'
   //   state - str state name as returned by get_all_active_sessions(GameID)
   //   city - str city name as returned by get_all_active_sessions(GameID)
   //   returns an array of active sessions eg
   //   [SessID0, SessID1, SessID2]
   }

   // Note: The _by_sessID functions below are probably going to mostly be run
   // in a row, so if its more efficient to input and output whole lists, that
   // is fine too.
   static get_features_by_sessID(callback, sessID, features=null){
   //   returns the features of specific (callback, active) sessID.
   //   takes optional argument features which if not null, is an array of feature names
   //   specifying which features to return. this would be like:
   //   ['GameStart','Fail','GameEnd'].
   //   Returns list of features in JSON format
   }

   static get_feature_names_by_game(callback, gameID){
   //   returns all feature names of that game (callback, any format is fine)
   }

   static get_predictions_by_sessID(callback, sessID, predictions=null){
   //   returns the predictions of specific (callback, active) sessID.
   //   takes optional argument predictions which if not null, is an array of prediction names
   //   specifying which predictions to return. this would be like:
   //   ['probability to finish lv3' etc.].
   //   Returns list of predictions in JSON format
   }

   static get_prediction_names_by_game(callback, gameID){
   //   returns all prediction names of that game (any format is fine)
   }

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
}
