class Server
{
    static getGreeting()
    {
        var req = new XMLHttpRequest();
        req.onreadystatechange = function()
        {
            if (this.readyState == 4 && this.status == 200)
            {
                return this.responseText;
            }
        }
        req.open("POST", "realtime.py", true);
        req.send("method=say_hello");
    }
}
