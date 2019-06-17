var height = 350;
var width = 600;
var marker = '';

function createMap() {

    document.getElementById('parent').innerHTML = "<div id='map'> <div id='plot' class='my-plot-style'></div>";

    return L.map("map", {
          center: [43.6532, -79.3832],
          zoom: 12,
          layers: [
              L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
                attribution: "Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
                maxZoom: 18,
                id: "mapbox.streets",
                accessToken: 'pk.eyJ1IjoiYXJ0ZW1sb2IiLCJhIjoiY2llbmZ0MXI1MGM4YnNrbTI0dW94b3ltcCJ9.pHrURjSshpLct5AJ_Nt8MA'
              })
          ]
    });
}

function createMarkers(response) {
    var map = createMap();
    var popup_stmt = "";
    for (data in response){
        marker = L.marker(response[data].coords, {
             title: response[data].address
             
         })
         popup_stmt=popup_stmt+"<p><u><b>Address:</b> ";
         for(d in response[data].data){
         console.log(response[data].data[d])
             popup_stmt=popup_stmt+response[data].address+"</u></p><p><b>Fine: $</b>"+response[data].data[d].fine_amount+"</p><p><b>Infraction Description: </b>"+response[data].data[d].infraction_description+"</p><p>" +response[data].data[d].total_fines+"</p>    "
         };
        marker.bindPopup(popup_stmt).addTo(map);
    }
}

function createHeatMap(response){
    var map = createMap();
    var heatArray=[];
    for(data in response){
        for(d in response[data].data){
        heatArray.push(response[data].coords)
        } 
    }
    var heat = L.heatLayer(heatArray, {
        radius: 20,
        blur: 35
      }).addTo(map);
}

function getFilteredData() {
    var url = "/api/filter";
    var ticket_type = document.getElementById('selDescOpt').value;
    var address = document.getElementById('address').value;
    var time = document.getElementById('time').value;
    var date = document.getElementById('date').value;

    var userFilter = {'ticket_type':ticket_type,'address':address,'time':time,'date':date};

    d3.json(url, {
        method:"POST",
        header: {
            "Content-type": "application/json; charset=UTF-8"
        },
        body: JSON.stringify(userFilter)
    }).then(function(response) {
        var trace_data = [];
        var placeholder_address =[];
        var popup_stmt = "";

        createHeatMap(response);

        //var optionVal = document.getElementById('selDescOpt').value;

        console.log(userFilter)

        if (
            userFilter['ticket_type'] != '' ||
            userFilter['address'] != '' ||
            userFilter['time'] != '' ||
            userFilter['date'] != ''
            ) {
            createMarkers(response);
            scatterPlot(response);

        } else {
            barPlot(response);
            console.log('no value');
        }
    })
}

function barPlot(response) {
    var trace1 = {
      x: ['giraffes', 'orangutans', 'monkeys'],
      y: [20, 14, 23],
      name: 'SF Zoo',
      type: 'bar'
    };

    var trace2 = {
      x: ['giraffes', 'orangutans', 'monkeys'],
      y: [12, 18, 29],
      name: 'LA Zoo',
      type: 'bar'
    };

    var data = [trace1, trace2];

    var layout = {
        barmode : 'stack',
        title:'Bar Data',
        height: height,
        width: width,
        margin: {
            l: 60,
            r: 20,
            b: 60,
            t: 70,
            pad: 10
        },
        paper_bgcolor:'rgba(171, 205, 239, 0.8)',
        plot_bgcolor:'rgba(171, 205, 239, 0.8)'
    }

    Plotly.newPlot('plot', data, layout);
}
function colorPicker(tickets){
    if(tickets>400){
        return 'maroon'
    }
    else if(tickets>300){
        return 'orangered'
    }
    else if (tickets>200){
        return 'gold'
    }
    else if (tickets>100){
        return 'green'
    }
    else{
        return 'navy'
    }
}

function scatterPlot(response) {
    var plotData = [];
    var plotNameAddress = [];
    var x = [];
    var y = [];
    var text=[];
    var circleSize = [];
    color = [];

    for (addressData in response) {
        for ( addressDataCount in response[addressData].data){
            x.push(response[addressData].address);
            circleSize.push(response[addressData].data[addressDataCount]['total_fines']);
            y.push(response[addressData].data[addressDataCount]['fine_amount']);
            color.push(colorPicker(response[addressData].data[addressDataCount]['total_fines']));
        }
    }

    plotData.push({
        'mode': "markers",
        'marker': {
            size: circleSize,
            'color': color,
            'line': color
        },
        'name': "high jump",
        'type': "scatter",
        'x':x,
        'y':y
    });

    var layout = {
        hovermode:'closest',
            title:'Parking Data',
            height: height,
            width: width,
            margin: {
                l: 60,
                r: 20,
                b: 60,
                t: 70,
                pad: 10
            },
            paper_bgcolor:'rgba(171, 205, 239, 0.8)',
            plot_bgcolor:'rgba(171, 205, 239, 0.8)'
    };

    Plotly.newPlot("plot", plotData, layout);
}

getFilteredData();