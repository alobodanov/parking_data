function getData() {

  var url = "/api/data";

  d3.json(url).then(function(response) {

    console.log(response);

    var myMap = L.map("map", {
      center: [43.6532, -79.3832],
      zoom: 12
    });

    L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
      attribution: "Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
      maxZoom: 18,
      id: "mapbox.streets",
      accessToken: 'pk.eyJ1IjoiYXJ0ZW1sb2IiLCJhIjoiY2llbmZ0MXI1MGM4YnNrbTI0dW94b3ltcCJ9.pHrURjSshpLct5AJ_Nt8MA'
    }).addTo(myMap);


    var layout = {
      scope: "usa",
      showlegend: false,
      width:100,
      height:100,
      geo: {
        scope: "usa",
        projection: {
          type: "albers usa"
        },
        showland: true,
        landcolor: "rgb(217, 217, 217)",
        subunitwidth: 1,
        countrywidth: 1,
        subunitcolor: "rgb(255,255,255)",
        countrycolor: "rgb(255,255,255)"
      }
    };

    var data = '';

    for (data in response){
        var marker = L.marker(response[data].coords, {
          title: response[data].address
        }).bindPopup("<h1>" +response[data].address +"</h1><hr><h3>" +response[data].date_of_infraction +"</h3><hr><h3>" +response[data].infraction_code +"</h3><hr><h3>" +response[data].infraction_description +"</h3><hr><h3>" +response[data].set_fine_amount +"</h3><hr><h3>" +response[data].time_of_infraction +"</h3>").addTo(myMap);

    }


    Plotly.newPlot("plot", response, layout);

  });
}


function getTicketDescription(){
    var url = '/api/description';

    d3.json(url).then(function(response) {
        console.log(response);

    });

}

getData();
getTicketDescription();