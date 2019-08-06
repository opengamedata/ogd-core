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
}
