var height = 300;
var width = 500;

function getData() {
  var url = "/api/data";

  d3.json(url).then(function(response) {
    let myMap = L.map("map", {
      center: [43.6532, -79.3832],
      zoom: 12
    });

    L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
      attribution: "Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
      maxZoom: 18,
      id: "mapbox.streets",
      accessToken: 'pk.eyJ1IjoiYXJ0ZW1sb2IiLCJhIjoiY2llbmZ0MXI1MGM4YnNrbTI0dW94b3ltcCJ9.pHrURjSshpLct5AJ_Nt8MA'
    }).addTo(myMap);

    var data = '';

    for (data in response){
        var marker = L.marker(response[data].coords, {
          title: response[data].address
        }).bindPopup("<h1>" +response[data].address +"</h1><hr><h3>" +response[data].date_of_infraction+"</h3><hr><h3>" +response[data].infraction_code +"</h3><hr><h3>" +response[data].infraction_description +"</h3><hr><h3>" +response[data].set_fine_amount +"</h3><hr><h3>" +response[data].time_of_infraction +"</h3>").addTo(myMap);
    }

    var myPlot = document.getElementById('plot'),
        d3 = Plotly.d3,
        N = 16,
        x = d3.range(N),
        y = d3.range(N).map( d3.random.normal() ),
        data = [ { x:x, y:y, type:'scatter',
                mode:'markers', marker:{size:16} } ],
        layout = {
            hovermode:'closest',
            title:'Parking Data',
            height: height,
            width: width,
            paper_bgcolor:'rgba(171, 205, 239, 0.8)',
            plot_bgcolor:'rgba(171, 205, 239, 0.8)'
         };
    Plotly.newPlot("plot", response, layout);

    myPlot.on('click', function(data){
        height = 600;
        width = 800;
    });
  });
}

function getFilteredData() {
    var url = "/api/filter";
    var ticket_type = document.getElementById('selDescOpt').value;
    var address = document.getElementById('address').value;
    var time = document.getElementById('time').value;
    var date = document.getElementById('date').value;

    d3.json(url, {
        method:"POST",
        header: {
            "Content-type": "application/json; charset=UTF-8"
        },
        body: JSON.stringify({'ticket_type':ticket_type,'address':address,'time':time,'date':date})
    }).then(function(response) {
        document.getElementById('map').innerHTML = "";
        let myMap = L.map("map", {
          center: [43.6532, -79.3832],
          zoom: 12
        });

        L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
          attribution: "Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
          maxZoom: 18,
          id: "mapbox.streets",
          accessToken: 'pk.eyJ1IjoiYXJ0ZW1sb2IiLCJhIjoiY2llbmZ0MXI1MGM4YnNrbTI0dW94b3ltcCJ9.pHrURjSshpLct5AJ_Nt8MA'
        }).addTo(myMap);

        myMap.removeLayer(marker);

        if (response[data].date_of_infraction){
            for (data in response){
                var marker = L.marker(response[data].coords, {
                  title: response[data].address
                }).bindPopup("<h1>" +response[data].address +"</h1><hr><h3>" +response[data].date_of_infraction +"</h3><hr><h3>" +response[data].infraction_code +"</h3><hr><h3>" +response[data].infraction_description +"</h3><hr><h3>" +response[data].set_fine_amount +"</h3><hr><h3>" +response[data].time_of_infraction +"</h3>").addTo(myMap);
            }

            var myPlot = document.getElementById('plot'),
                d3 = Plotly.d3,
                N = 16,
                x = d3.range(N),
                y = d3.range(N).map( d3.random.normal() ),
                data = [ { x:x, y:y, type:'scatter',
                        mode:'markers', marker:{size:16} } ],
                layout = {
                    hovermode:'closest',
                    title:'Parking Data',
                    height: height,
                    width: width,
                 };

            Plotly.newPlot("plot", response, layout);

            myPlot.on('plotly_click', function(data){
                height = 600;
                width = 800;
            });

            var data = '';

            if (response[data].date_of_infraction){
                for (data in response){
                    var marker = L.marker(response[data].coords, {
                        title: response[data].address
                    }).bindPopup("<h1>" +response[data].address +"</h1><hr><h3>" +response[data].date_of_infraction +"</h3><hr><h3>" +response[data].infraction_code +"</h3><hr><h3>" +response[data].infraction_description +"</h3><hr><h3>" +response[data].set_fine_amount +"</h3><hr><h3>" +response[data].time_of_infraction +"</h3>").addTo(myMap);
                }
            } else {
                for (data in response){
                    var marker = L.marker(response[data].coords, {
                        title: response[data].address
                    }).bindPopup("<h1>" +response[data].address +"</h1><hr><h3>" +response[data].total_fines +"</h3><hr><h3>" +response[data].average_fine).addTo(myMap);
                }
            }
        }
  });
}

function changePlotSize(){
    this.height = 600;
    this.width = 800;
}

getData();


