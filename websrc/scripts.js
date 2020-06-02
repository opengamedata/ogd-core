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
    let table_name;
    generateTableHead(table, headers);
    if(start)
    {
      generateTable(table, Object.values(tables)[0], headers);
      generate_options();
      console.log(tables)
      document.getElementById("readme_fname").href = `data/${Object.keys(tables)[0]}/readme.md`;
    }
    else
    {
      generateTable(table, tables[value], headers);
      document.getElementById("readme_fname").href = `data/${value}/readme.md`;
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
            if(set["sql"] != null){
            var raw_link = document.createElement('a');
            var linkText = document.createTextNode("Raw");
            raw_link.appendChild(linkText);
            raw_link.title = "Raw";
            raw_link.href = set["raw"];
            cell.appendChild(raw_link);
            cell.append(document.createTextNode(' - '))
                        }
                        
            if(set["sql"] != null){
            var sql_link = document.createElement('a');
            var linkText = document.createTextNode("Processed");
            sql_link.appendChild(linkText);
            sql_link.title = "Processed";
            sql_link.href = set["proc"];
            cell.appendChild(sql_link);
            cell.append(document.createTextNode(' - '))
            }

            if(set["sql"] != null){
                        var sql_link = document.createElement('a');
            var linkText = document.createTextNode("SQL");
            sql_link.appendChild(linkText);
            sql_link.title = "SQL Dump";
                        sql_link.href = set["sql"];
                                    cell.appendChild(sql_link);

            }
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
  select.onchange = function(){if (this.value) change_tables(this.value);};
  for(table_name in tables){
    var option = document.createElement("option");
    option.text = table_name;
    select.add(option);
  }
}

change_tables("CRYSTAL",true);
