class Server
{
    static getGreeting(callback)
    {
        var req = new XMLHttpRequest();
        req.onreadystatechange = function()
        {
            if (this.readyState == 4 && this.status == 200)
            {
               callback(this.responseText);
            }
        }
        req.open("POST", "realtime.py", true);
        req.send("method=say_hello");
    }
}
