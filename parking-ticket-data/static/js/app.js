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

    for (data in response){
        marker = L.marker(response[data].coords, {
             title: response[data].address
         }).bindPopup("<p><u><b>Address:</b> "+response[data].address+"</u></p><p><b>Fine: $</b>"+response[data].data[0].fine_amount+"</p><p><b>Infraction Description: </b>"+response[data].data[0].infraction_description+"</p><p>" +response[data].set_fine_amount+"</p><p></p>").addTo(map);
    }
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

        createMarkers(response);

        var optionVal = document.getElementById('selDescOpt').value;

        console.log(userFilter)

        if (
            userFilter['ticket_type'] != '' ||
            userFilter['address'] != '' ||
            userFilter['time'] != '' ||
            userFilter['date'] != ''
            ) {
            scatterPlot(response);

        } else {
            barPlot(response);
            console.log('no value');
        }







//        try {
//            console.log(response[0])
//            if (response[0].coords1!="undefined"){
//                console.log(response[0]);
//                 for (data in response){
//                    marker = L.marker(response[data].coords1, {
//                         title: response[data].address
//                     }).bindPopup("<h1>" +response[data].address +"</h1><hr><h3>" +response[data] +"</h3><hr><h3>" +response[data].infraction_description +"</h3><hr><h3>" +response[data].set_fine_amount +"</h3><hr><h3>" +response[data].time_of_infraction +"</h3>").addTo(map);
//                }
//                var myPlot = document.getElementById('plot'),
//                d3 = Plotly.d3,
//                N = 16,
//                x = d3.range(N),
//                y = d3.range(N).map( d3.random.normal() ),
//                data = [ { x:x, y:y, type:'scatter',
//                        mode:'markers', marker:{size:16} } ],
//                layout = {
//                    hovermode:'closest',
//                    title:'Parking Data',
//                    height: height,
//                    width: width,
//                    margin: {
//                        l: 30,
//                        r: 20,
//                        b: 30,
//                        t: 70,
//                        pad: 10
//                    },
//                    paper_bgcolor:'rgba(171, 205, 239, 0.8)',
//                    plot_bgcolor:'rgba(171, 205, 239, 0.8)'
//                 };
//                Plotly.newPlot("plot", response, layout);
//
//            }
//        } catch (error) {
//            console.log(error);
//            if (error.name === 'TypeError'){
//                for (data in response){
//                    if (placeholder_address.indexOf(response[data].address)>-1 && data==response.length-1){
//                        console.log("if");
//                        trace1.y=response[data].data.fine_amount;
//                            trace1.marker.size=response[data].data.total_fines;
//                            console.log(trace1);
//                            popup_stmt = popup_stmt+"<hr><h2> Ticket Type:" +response[data].data.infraction_description+"</h2><hr><h3> Number of Fines: " +response[data].data.total_fines +"</h3>";
//                            marker.bindPopup(popup_stmt).addTo(map);
//                    } else if (placeholder_address.indexOf(response[data].address)>-1){
//
//                        trace1.y=response[data].data.fine_amount;
//                        trace1.marker.size=response[data].total_fines;
//                        popup_stmt = popup_stmt+"<hr><h2> Ticket Type:" +response[data].data.infraction_description+"</h2><hr><h3> Number of Fines: " +response[data].data.total_fines +"</h3>";
//                        console.log(trace1)
//                        trace_data.push(trace1);
//                        console.log("trace_data:")
//                        console.log(trace_data)
//                    } else if(response[data].address != placeholder_address && placeholder_address.length ==[]){
//                        console.log("else if2");
//                        console.log(response[data].address);
//                        placeholder_address.push(response[data].address)
//                        console.log(placeholder_address);
//                        console.log(popup_stmt);
//                        popup_stmt="<h1>" +response[data].address +"</h1>";
//                        console.log(popup_stmt);
//                        trace1.y=response[data].data.fine_amount;
//                        trace1.marker.size=response[data].data.total_fines;
//                        popup_stmt = popup_stmt+"<hr><h2> Ticket Type:" +response[data].data.infraction_description+"</h2><hr><h3> Number of Fines: " +response[data].data.total_fines +"</h3>";
//                        trace1.x=response[data].address;
//                        marker = L.marker(response[data].coords, {
//                        title: response[data].address
//
//                        })
//                    } else if(response[data].address != placeholder_address && placeholder_address.length ==[] && response.length==1){
//                        console.log("else if2");
//                        console.log(response[data].address);
//
//                        placeholder_address.push(response[data].address)
//                        console.log(placeholder_address);
//                        console.log(popup_stmt);
//                        popup_stmt="<h1>" +response[data].address +"</h1>";
//                        console.log(popup_stmt);
//                        trace1.y=response[data].data.fine_amount;
//                        trace1.marker.size=response[data].data.total_fines;
//                        popup_stmt = popup_stmt+"<hr><h2> Ticket Type:" +response[data].data.infraction_description+"</h2><hr><h3> Number of Fines: " +response[data].data.total_fines +"</h3>";
//                        trace1.x=response[data].address;
//                        marker = L.marker(response[data].coords, {
//                            title: response[data].address
//                        })
//                        marker.bindPopup(popup_stmt);
//                    } else if(response[data].address!=placeholder_address[data-1] && data==response.length-1){
//                        console.log("else if4");
//                        console.log(response[data].address);
//                        console.log(response[data].address);
//                        marker.bindPopup(popup_stmt).addTo(map);
//                        placeholder_address.push(response[data].address)
//                        console.log(popup_stmt);
//                        popup_stmt="<h1>" +response[data].address +"</h1>";
//                        console.log(popup_stmt);
//                        trace1.y=response[data].data.fine_amount;
//                        trace1.marker.size=response[data].data.total_fines;
//                        popup_stmt = popup_stmt+"<hr><h2> Ticket Type:" +response[data].data.infraction_description+"</h2><hr><h3> Number of Fines: " +response[data].data.total_fines +"</h3>";
//                        trace1.x=response[data].address;
//                        marker = L.marker(response[data].coords, {
//                            title: response[data].address
//                        });
//                        marker.bindPopup(popup_stmt).addTo(map);
//                    } else if(response[data].address!=placeholder_address[data-1] && data<response.length){
//                        console.log("else if3");
//                        console.log(response[data].address);
//                        console.log(response[data].address)
//                        marker.bindPopup(popup_stmt).addTo(map);
//                        placeholder_address.push(response[data].address)
//                        console.log(popup_stmt);
//                        popup_stmt="<h1>" +response[data].address +"</h1>";
//                        console.log(popup_stmt);
//                        trace1.y=response[data].data.fine_amount;
//                        trace1.marker.size=response[data].data.total_fines;
//                        popup_stmt = popup_stmt+"<hr><h2> Ticket Type:" +response[data].data.infraction_description+"</h2><hr><h3> Number of Fines: " +response[data].data.total_fines +"</h3>";
//                        trace1.x=response[data].address;
//                        marker = L.marker(response[data].coords, {
//                        title: response[data].address})
//                        } else {
//                            console.log("else")
//                            trace1.y=response[data].data.fine_amount;
//                            trace1.marker.size=response[data].data.total_fines;
//                            popup_stmt = popup_stmt+"<hr><h2> Ticket Type:" +response[data].data.infraction_description+"</h2><hr><h3> Number of Fines: " +response[data].data.total_fines +"</h3>";
//                            marker.bindPopup(popup_stmt).addTo(map);
//
//                    }
//                    var x=[];
//                    var y=[];
//                    var s=[];
//                    for (t in trace_data){
//                        console.log(t);
//                        x.push(trace_data[t].x);
//                        y.push(trace_data[t].y);
//                        //s.push(t.marker.size);
//                    }
//                    var t1 =[{x:x,y:y,type:'scatter',
//                        mode:'markers',
//                        //marker:{size:s}
//                    }]
//
//                   trace_data.push(trace1);
//                   console.log("trace_data:")
//                        console.log(t1)
//
//                }
//
//
//
//        /* var myPlot = document.getElementById('plot'),
//            d3 = Plotly.d3,
//            data = [ {
//                x:trace1.x,
//                y:trace1.y,
//                type:'scatter',
//                mode:'markers',
//                marker:{size: trace1.size} }]
//            layout = {
//                hovermode:'closest',
//                title:'Parking Data',
//                height: height,
//                width: width,
//                margin: {
//                    l: 20,
//                    r: 20,
//                    b: 30,
//                    t: 70,
//                    pad: 10
//                },
//                paper_bgcolor:'rgba(171, 205, 239, 0.8)',
//                plot_bgcolor:'rgba(171, 205, 239, 0.8)'
//             };
//
//        }
//
//    } */
//                var layout = {
//                        hovermode:'closest',
//                                title:'Parking Data',
//                                height: height,
//                                width: width,
//                                margin: {
//                                    l: 20,
//                                    r: 20,
//                                    b: 30,
//                                    t: 70,
//                                    pad: 10
//                                },
//                                paper_bgcolor:'rgba(171, 205, 239, 0.8)',
//                                plot_bgcolor:'rgba(171, 205, 239, 0.8)'
//
//                };
//                console.log(trace_data);
//                Plotly.newPlot("plot", t1, layout);
//
//                var data = '';
//            }
//        }
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

function scatterPlot(response) {
    var plotData = [];
    var plotNameAddress = [];
    var x = [];
    var y = [];
    var circleSize = [];

    for (addressData in response) {
        x.push(response[addressData].address);
        circleSize.push(response[addressData].data[0]['fine_amount'])

        for ( addressDataCount in response[addressData].data){
            y.push(response[addressData].data[addressDataCount]['fine_amount']);
        }
    }

    plotData.push({
        'mode': "markers",
        'marker': {
            size: circleSize,
            'color': ['rgb(93, 164, 214)', 'rgb(255, 144, 14)',  'rgb(44, 160, 101)', 'rgb(255, 65, 54)']
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