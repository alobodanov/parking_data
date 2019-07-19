var height = 750;
var width = 1050;

function getFilteredData(chartTypeData) {
    var url = "/api/prediction/"+chartTypeData;

    d3.json(url, {
        method:"GET",
        header: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then(function(response) {
        console.log(response)
        var title_name = '';

        if (chartTypeData == 'location'){
            title_name = 'Location'
        } else if (chartTypeData == 'fine_count') {
            title_name = 'Fine Count'
        } else {
            title_name = 'Fee'
        }

        var layout = {
            'barmode': "scatter",
            hovermode:'closest',
            title: title_name,
            height: height,
            width: width
        };

        var data = [
            {
                x: response[0].x,
                y: response[0].y,
                type: 'scatter',
                name: 'Actual'
            },
            {
                x: response[1].x,
                y: response[1].y,
                type: 'scatter',
                name: 'Prediction'
            }
        ];

    Plotly.newPlot('plotChart', data, layout);


    })
}

getFilteredData('fine_count');