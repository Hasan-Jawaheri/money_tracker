var AppData = null;
var DataPointsMap = {};
var TransactionHistory = [];
var HighlightedTransactionIndices = [];
var CurrentZoomBounds = [];

document.addEventListener('DOMContentLoaded', function() {
    AppData = __appdata;
    delete __appdata;
    
    TransactionHistory = Object.keys(AppData).map(accountName => AppData[accountName].transactions.map(tx => {return {...tx, date: new Date(tx.date), account: accountName}})).reduce((a, b) => a.concat(b), []);
    var currentTotalBalances = {};
    var datapoints = [];
    TransactionHistory.sort((a,b) => a.date - b.date).forEach((tx, txi) => {
        tx.indexInHistory = txi;
        if (!(tx.account in currentTotalBalances))
            currentTotalBalances[tx.account] = AppData[tx.account].opening_balance;
        currentTotalBalances[tx.account] += tx.delta

        var currentTotalBalance = Object.keys(currentTotalBalances).map(key => currentTotalBalances[key]).reduce((a, b) => a+b, 0);

        if (datapoints.length > 0 && datapoints[datapoints.length-1].x.getTime() == tx.date.getTime()) {
            datapoints[datapoints.length-1].y = currentTotalBalance;
            datapoints[datapoints.length-1].transactions.push(tx);
        } else {
            datapoints.push({
                x: tx.date,
                y: currentTotalBalance, // total
                totalBalance: currentTotalBalance,
                currentTotalBalances: JSON.parse(JSON.stringify(currentTotalBalances)),
                transactions: [tx],
            });
        }
        if (datapoints[datapoints.length-1].transactions.map(tx => tx.desc).reduce((a, b) => a+b, "").toLowerCase().indexOf("salary") >= 0)
            datapoints[datapoints.length-1].indexLabel = "salary";
        DataPointsMap[datapoints[datapoints.length-1].x] = datapoints[datapoints.length-1];
    });

    var chart = new CanvasJS.Chart("myChart", {
        axisX:{
            title: "",
            gridThickness: 2
        },
        axisY: {
            title: "Foloos"
        },
        data: [{
            type: "area",
            dataPoints: datapoints,
            name: "Total",
            click: e => onDatapointClicked(DataPointsMap[e.dataPoint.x]),
        }],
        zoomEnabled: true,
        animationEnabled: true,
        rangeChanging: e => onRangeChanged(e.axisX[0].viewportMinimum, e.axisX[0].viewportMaximum)
    });

    chart.render();

    updateTable();
}, false);

function onDatapointClicked(dp) {
    HighlightedTransactionIndices = dp.transactions.map(tx => tx.indexInHistory);
    updateTable();
}

function onRangeChanged(x0, x1) {
    console.log(x0, x1);
    CurrentZoomBounds = [];
    if (x0 && x1) {
        for (var i = 0; i < TransactionHistory.length; i++) {
            var tx = TransactionHistory[i];
            if (tx.date.getTime() >= x0 && CurrentZoomBounds.length == 0)
                CurrentZoomBounds.push(Math.max(i-1, 0));
            else if (tx.date.getTime() > x1 && CurrentZoomBounds.length == 1)
                CurrentZoomBounds.push(Math.min(i+1, TransactionHistory.length));
        }
    }
    updateTable();
}

function updateTable() {
    tableBody = document.getElementById("table-body");
    newHTML = "";

    scrolled = false;
    if (CurrentZoomBounds.length == 0)
        CurrentZoomBounds = [0, TransactionHistory.length];

    TransactionHistory.slice(CurrentZoomBounds[0], CurrentZoomBounds[1]).forEach(tx => {
        dp = DataPointsMap[tx.date]
        trClass = HighlightedTransactionIndices.indexOf(tx.indexInHistory) >= 0 ? "tr-highlight" : "";
        deltaClass = tx.delta > 0 ? "delta-positive" : "delta-negative";

        if (trClass != "" && !scrolled) {
            scrolled = true;

        }

        newHTML += `
            <tr class="` + trClass + `">
                <td>` + tx.date.toDateString() + `</td>
                <td>` + tx.account + `</td>
                <td>` + tx.desc.split('\n').map(line => "<div>" + line + "</div>").reduce((a, b) => a + b, "") + `</td>
                <td class="` + deltaClass + `">` + tx.delta + `</td>
                <td>` + dp.totalBalance.toFixed(2) + `</td>
            </tr>
        `;
    });

    tableBody.innerHTML = newHTML;
}
