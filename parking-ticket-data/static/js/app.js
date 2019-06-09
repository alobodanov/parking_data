function buildPlot() {

  var url = "/api/data";

  d3.json(url).then(function(response) {

    console.log(response);

    var data = response;

    var myMap = L.map("map", {
      center: [45.52, -122.67],
      zoom: 13
    });

//    L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
//      attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
//      maxZoom: 18,
//      id: "mapbox.streets",
//      accessToken: 'pk.eyJ1IjoiYXJ0ZW1sb2IiLCJhIjoiY2llbmZ0MXI1MGM4YnNrbTI0dW94b3ltcCJ9.pHrURjSshpLct5AJ_Nt8MA'
//    }).addTo(myMap);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(myMap);

    var marker = L.marker([45.52, -122.67], {
      title: "My First Marker"
    }).addTo(myMap);

//    marker.bindPopup("Hello There!");

    var layout = {
      scope: "usa",
      title: "Pet Pals",
      showlegend: false,
      height: 600,
            // width: 980,
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

    Plotly.newPlot("plot", data, layout);
  });
}

buildPlot();
