var height = 350;
var width = 800;
var marker = '';
var optionVal = document.getElementById('selDescOpt').value;
var map = '';

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
        popup_stmt = "";
        marker = L.marker(response[data].coords, {
             title: response[data].address
         })
         popup_stmt=popup_stmt+"<p><u><b>Address:</b> ";
         for(d in response[data].data){
             popup_stmt = popup_stmt+response[data].address+"</u></p><p><b>Infraction Description: </b>"+response[data].data[d].infraction_description+"</p><p><b>Fine: $</b>"+response[data].data[d].fine_amount+"</p><p><b>Total Fines:</b> " +response[data].data[d].total_fines+"</p>    "
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
    var time_from = document.getElementById('timeFrom').value;
    var time_to = document.getElementById('timeTo').value;
    var date = document.getElementById('date').value;

    if ((time_from && !time_to) || (!time_from && time_to)) {
        document.getElementById('errorFromTo').style.display = 'block'
        return;

    } else {
        document.getElementById('errorFromTo').style.display = 'none';
    }

    var userFilter = {
        'ticket_type': ticket_type,
        'address': address,
        'time_from': time_from,
        'time_to': time_to,
        'date': date
    };

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

        if (
            userFilter['ticket_type'] != '' ||
            userFilter['address'] != '' ||
            userFilter['time_from'] != '' ||
            userFilter['time_to'] != '' ||
            userFilter['date'] != ''
            ) {
            createMarkers(response);
            barPlot(response);
        } else {
            createHeatMap(response);
            hPlot(response);
        }
    })
}

function barPlot(response) {
    var plotData = [];
    var plotNameAddress = [];
    var x = [];
    var y = [];
    var text=[];
    var circleSize = [];
    color = [];

    for (addressData in response) {
        for ( addressDataCount in response[addressData].data){
            plotData.push({
                'type': "bar",
                'x':[response[addressData].address],
                'y':[response[addressData].data[addressDataCount]['total_fines']],
                'name':response[addressData].data[addressDataCount]['infraction_description']
            });
        }
    }

    var layout = {
        'barmode': "stack",
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

    Plotly.newPlot('plot', plotData, layout);
}

function hPlot(response){

    var plotData = [];
    var plotNameAddress = [];
    var x = [];
    var y = [];
    var text=[];
    var circleSize = [];
    color = [];

      response.sort(function(a, b) {
        return parseFloat(b.data.length) - parseFloat(a.data.length);
      });

      response = response.slice(0, 10);
      response.reverse();

      for (addressData in response) {
        for ( addressDataCount in response[addressData].data){
            x.push(response[addressData].address);
            y.push(response[addressData].data.length);
        }
    }

    plotData.push({
        type: "bar",
        orientation: "h",
        'x':y,
        'y':x,
    });

    var layout = {
        'barmode': "bar",
        hovermode:'closest',
        title:'Parking Data',
        height: height,
        width: width,
        margin: {
            l: 150,
            r: 0,
            b: 30,
            t: 70,
            pad: 10
        },
        paper_bgcolor:'rgba(171, 205, 239, 0.8)',
        plot_bgcolor:'rgba(171, 205, 239, 0.8)'
    };

    Plotly.newPlot('plot', plotData, layout);
}

getFilteredData();