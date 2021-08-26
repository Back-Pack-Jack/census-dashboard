
    function random_rgba() {
        var o = Math.round, r = Math.random, s = 255;
        return 'rgba(' + o(r()*s) + ',' + o(r()*s) + ',' + o(r()*s) + ',' + r().toFixed(1) + ')';
    }

    function createCanvas(parent, width, height) {
        var canvas = document.getElementById("inputCanvas");
        canvas.context = canvas.getContext('2d');
        return canvas;
    }

    export function createGraph(datetime, bicycle, bus, car, motorbike, person, truck) {
        const mob_ctx = document.getElementById('mobilityChart').getContext('2d');
        var date = datetime;
        const mobChart = new Chart(mob_ctx, {
            type: 'line',
            data: {
                labels: date,
                datasets: [
                {   
                    label: 'Bicycles',
                    data: bicycle,
                    backgroundColor: color1,
                    borderColor: color1,
                    borderWidth: 1
                },
                {
                    label: 'Bus',
                    data: bus,
                    backgroundColor: color2,
                    borderColor: color2,
                    borderWidth: 1
                },
                {
                    label: 'Car',
                    data: car,
                    backgroundColor: color3,
                    borderColor: color3,
                    borderWidth: 1
                },
                {
                    label: 'Motorbike',
                    data: motorbike,
                    backgroundColor: color4,
                    borderColor: color4,
                    borderWidth: 1
                },
                {
                    label: 'Person',
                    data: person,
                    backgroundColor: color5,
                    borderColor: color5,
                    borderWidth: 1
                },
                {
                    label: 'Truck',
                    data: truck,
                    backgroundColor: color6,
                    borderColor: color6,
                    borderWidth: 1
                },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        
                    },
                }
            }
        });
    }