var tables;
var table;
var headers = {
  "start_date": "Start Date",
  "end_date": "End Date",
  "date_modified": "Date Modified",
  "Dataset ID": "Dataset ID",
  "sessions": "Sessions",
  "raw": "Downloads",

}
function change_tables(value, start=false) {
  let table = document.querySelector("table");
  table.innerHTML = '';
  jQuery.getJSON("/data/file_list.json",function(result){
    tables = result;
    let table = document.querySelector("table");
    generateTableHead(table, headers);
    if(start)
    {
      generate_options();
      generateTable(table, Object.values(tables)[0], headers);
    }
    else
    {
      generateTable(table, tables[value], headers);
    }
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
  setIDs = Object.keys(data)
  setIDs.sort((x,y) => Date.parse(data[y]["start_date"]) - Date.parse(data[x]["start_date"]))
  for (let setID of setIDs) {
    var set = data[setID]
    let row = table.insertRow();
    for (key in headers) {
      let cell = row.insertCell();
      var text = null;
      switch (key) {
        case "Dataset ID":
          text = document.createTextNode(setID);
          cell.appendChild(text);
          break;
        case "raw":
            var a = document.createElement('a');
            var linkText = document.createTextNode("Raw");
            a.appendChild(linkText);
            a.title = "Raw";
            a.href = set["raw"];
            cell.appendChild(a);
            cell.append(document.createTextNode(' - '))
            var a = document.createElement('a');
            var linkText = document.createTextNode("Processed");
            a.appendChild(linkText);
            a.title = "Processed";
            a.href = set["proc"];
            cell.appendChild(a);
          break;
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

change_tables("CRYSTAL",true);
