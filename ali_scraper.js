var product_name = "apple watch band";
var base_url = "https://www.aliexpress.com/wholesale?SortType=total_tranpro_desc";

var url = base_url + "&SearchText=" + product_name.split(" ").join("+");
var maxOrders = 100; // can be changed easily

var headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}

var ss = SpreadsheetApp.getActiveSpreadsheet();
var source = ss.getSheets()[0];

function determineEndPage(url) {
  var endPage;
  var pageContent = getHTML(url);
  var countString = getElementsByClassName(pageContent, "search-count")[0].getText();
  countString = countString.replace(/,/g, "");
  var results = parseInt(countString);
  if (results > 4800) {
    endPage = 100;
  }
  else if (results > 0 && results < 4800) {
    x = results / 48;
    endPage = Math.ceil(x);
  }
  return endPage;
}

function getHTML(url) {
  //var url = "https://www.aliexpress.com/"
  var content = UrlFetchApp.fetch(url, headers);
  //Logger.log("Content: "+content);
  var doc = Xml.parse(content, true);
  var bodyHtml = doc.html.body.toXmlString();
  doc = XmlService.parse(bodyHtml);
  return doc.getRootElement();
}

function getItemsOnPage(pageNum) {
  Logger.log("Page: "+pageNum);
  var pageContent = getHTML(url+"&page="+pageNum);  //hopefully no type error
  var listEle = getElementById(pageContent, "hs-below-list-items");  // mind the singularity!
  var itemsEle = getElementsByClassName(listEle, "item");
  var items = {};
  for (var i = 0; i < itemsEle.length; ++i) {
    var ele = itemsEle[i];
    var info = getElementsByClassName(ele, "info")[0];
    var name = getElementsByClassName(info, "history-item")[0].getText();
    var price = getElementsByClassName(info, "value")[0].getText();
    var ordersEle = getElementsByClassName(info, "order-num")[0];
    var ordersString = getElementsByTagName(ordersEle, "em")[0].getText().match(/\(([^)]+)\)/)[1];
    ordersString = ordersString.replace(/,/g, "");
    var orders = parseInt(ordersString);
    var link = getElementsByTagName(info, "a")[0].getAttribute("href").getValue();
    var tokens = link.split("?")[0].split("/");
    var id = parseInt(tokens[tokens.length-1].split(".")[0]);
    items[id] = {
      "name": name,
      "price": price,
      "link": link,
      "orders": orders
    };
    
    if (i==0) {
      var firstOrders = items[id].orders;
    }
  }
  return [items, firstOrders];
}

function getFirstEmptyRowWholeRow() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var range = sheet.getDataRange();
  var values = range.getValues();
  var row = 0;
  for (var row=0; row<values.length; row++) {
    if (!values[row].join("")) break;
  }
  return (row+1);
}

function putItems(items, startRow) {
    var keys = Object.keys(items);
    var itemsArray = [];
    var range = source.getRange("A"+startRow+":E"+(startRow+keys.length-1));
    Logger.log(range);
    Logger.log("Keyslength: "+keys.length);
    for(var i=0; i!=keys.length; ++i) {
        var id = keys[i];
        var item = items[id];
        itemsArray.push([id, item.name, item.price, item.link, item.orders]);
    }
    Logger.log("Height: "+itemsArray.length);
    range.setValues(itemsArray);
    //var column = source.getRange("D"+startRow+":D"+(startRow+keys.length-1));
    //column.setFormula('=HYPERLINK(D2:D, "link")');
}

function getItems(url) {
  var count = 2;
  Logger.log("Getting items");
  var endPage = determineEndPage(url);
  Logger.log("endpage: "+endPage);
  var firstOrders;
  var itemsOnPage;
  var items = {};
  for (var i=endPage; i>=1; --i) {
    Logger.log("Count: "+count);
    //Logger.log("Page number: "+i);
    try {
      var PageData = getItemsOnPage(i);
    } catch(e) {
      i++;
      Logger.log(e);
      Logger.log("Sleeping for a 5 seconds...\n");
      Utilities.sleep(6000);
      continue;
    }
    itemsOnPage = PageData[0];
    firstOrders = PageData[1];
    //Utilities.sleep(1000);
    var keys = Object.keys(itemsOnPage);
    Logger.log("firstOrders: "+firstOrders);
    if (firstOrders <= maxOrders) {
        for (var j = 0; j < keys.length; ++j) {
          var id = keys[j];
          items[id] = itemsOnPage[id];
        }
        putItems(itemsOnPage, count);
        count += keys.length;
        continue;
    }
    for (var j = 0; j < keys.length; ++j) {
        var id = keys[j];
        item = itemsOnPage[id];
        if (item['orders'] > maxOrders) {
            continue;
        }
        items[id] = item;
        putItems({id: item}, count);
        count++;
    }
    break;
  }
  return items;
}

function work() {
    Logger.log("putting Items");
    getItems(url);
}

//////////////////////////////////////////////////////////////////////////////////
function getElementsByClassName(element, classToFind) {  
  var data = [];
  var descendants = element.getDescendants();
  descendants.push(element);  
  for(i in descendants) {
    var elt = descendants[i].asElement();
    if(elt != null) {
      var classes = elt.getAttribute('class');
      if(classes != null) {
        classes = classes.getValue();
        if(classes == classToFind) data.push(elt);
        else {
          classes = classes.split(' ');
          for(j in classes) {
            if(classes[j] == classToFind) {
              data.push(elt);
              break;
            }
          }
        }
      }
    }
  }
  return data;
}

function getElementsByTagName(element, tagName) {  
  var data = [];
  var descendants = element.getDescendants();  
  for(i in descendants) {
    var elt = descendants[i].asElement();     
    if( elt !=null && elt.getName()== tagName) data.push(elt);      
  }
  return data;
}

function getElementById(element, idToFind) {  
  var descendants = element.getDescendants();  
  for(i in descendants) {
    var elt = descendants[i].asElement();
    if( elt !=null) {
      var id = elt.getAttribute('id');
      if( id !=null && id.getValue()== idToFind) return elt;    
    }
  }
}

function getRowData(row){
  var attributes = getElementsByClassName(row, "qmdata");
  var name = getElementsByTagName(attributes[0], "a")[0].getText();
  var sym = getElementsByTagName(attributes[1], "a")[0].getText();
  var exchange = attributes[6].getText();
  var sector = attributes[7].getText();
  var sheetRow = [[name, sym, exchange, sector]];
  return sheetRow;
}

function getVal(ele){
  return ele[0];
}

function scrapeContent() {
  var url = "http://marijuanaindex.com/marijuana-stock-universe/";
  var content = UrlFetchApp.fetch(url);
  var doc = Xml.parse(content, true);
  var bodyHtml = doc.html.body.toXmlString();
  doc = XmlService.parse(bodyHtml);
  var html = doc.getRootElement();
  //var html = doc.getRootElement();
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var source = ss.getSheets()[0];
  var prev_range_values = source.getRange("B2:B").getValues();
  var prev_values = prev_range_values.map(getVal);
  
  var rows = getElementsByClassName(html, "thisIsFromTheDatabase");
  for(var i=0; i!=rows.length; ++i){
    var range = source.getRange("A"+(i+2)+":D"+(i+2));
    row = rows[i];
    range.setValues(getRowData(row));
  }
  var new_range = source.getRange("B2:B");
  var newItems = [];
  var new_values = new_range.getValues().map(getVal);
  for each(var item in new_values){
    if (prev_values.indexOf(item) === -1){
      newItems.push(item);
    }
  }
  if (newItems.length > 0){  // New item added.
    var message = "New stock(s) found:\n\n" + newItems.join("\n") + "\n\nRegards,\nSamChatsBot";
    var subject = "New stock(s) found";
    var emailAddress = "ben@herzlcapital.com";
    MailApp.sendEmail(emailAddress, subject, message);
    MailApp.sendEmail("16ucc086@lnmiit.ac.in", subject, message); // For now, I'm adding it to ensure that it works as expected. Shall remove soon.
  }
}
