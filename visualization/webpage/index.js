var AppData = null;
var DataPointsMap = {};
var TransactionHistory = [];
var HighlightedTransactionIndices = [];
var CurrentZoomBounds = [];
var SelectedTransactionIndex = -1;

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
    onTransactionClicked(-1);
}, false);

function onDatapointClicked(dp) {
    HighlightedTransactionIndices = dp.transactions.map(tx => tx.indexInHistory);
    if (SelectedTransactionIndex >= 0)
        onTransactionClicked(SelectedTransactionIndex); // re-click will remove it
    updateTable();
}

function onRangeChanged(x0, x1) {
    console.log(x0, x1);
    CurrentZoomBounds = [];
    HighlightedTransactionIndices = [];
    if (x0 && x1) {
        for (var i = 0; i < TransactionHistory.length; i++) {
            var tx = TransactionHistory[i];
            if (tx.date.getTime() >= x0 && CurrentZoomBounds.length == 0)
                CurrentZoomBounds.push(Math.max(i-1, 0));
            else if (tx.date.getTime() > x1 && CurrentZoomBounds.length == 1)
                CurrentZoomBounds.push(Math.min(i+1, TransactionHistory.length));
        }
    }
    if (SelectedTransactionIndex >= 0 && CurrentZoomBounds.length > 0) {
        if (SelectedTransactionIndex < CurrentZoomBounds[0] || SelectedTransactionIndex >= CurrentZoomBounds[1])
            onTransactionClicked(SelectedTransactionIndex); // re-click will remove it
    }

    updateTable();
}

function onTransactionClicked(txi) {
    if (SelectedTransactionIndex == txi)
        SelectedTransactionIndex = -1;
    else
        SelectedTransactionIndex = txi;
    
    if (SelectedTransactionIndex == -1) {
        document.getElementById("tx-table-container").className = "table-responsive col-md-12";
        document.getElementById("tx-container").className = "";
        document.getElementById("tx-container").style.display = "none";
    } else {
        document.getElementById("tx-table-container").className = "table-responsive col-md-8";
        document.getElementById("tx-container").className = "col-md-4";
        document.getElementById("tx-container").style.display = "block";

        updateCurrentTransaction(txi);
    }
    updateTable();
}

function updateCurrentTransaction(txi) {
    document.getElementById("tx-filename").innerHTML = TransactionHistory[txi].filename;
    document.getElementById("tx-balances").innerHTML = "<ul>" + Object.keys(DataPointsMap[TransactionHistory[txi].date].currentTotalBalances).map(
        account_name => "<li><span style=\"font-weight: bold\">" + account_name + ": </span>" + DataPointsMap[TransactionHistory[txi].date].currentTotalBalances[account_name] + "</li>"
    ) + "</ul>";
}

function updateTable() {
    tableBody = document.getElementById("table-body");
    newHTML = "";

    var scrolled = false;
    var scrollToId = "";
    if (CurrentZoomBounds.length == 0)
        CurrentZoomBounds = [0, TransactionHistory.length];

    TransactionHistory.slice(CurrentZoomBounds[0], CurrentZoomBounds[1]).forEach(tx => {
        var dp = DataPointsMap[tx.date];
        var isHighlighted = HighlightedTransactionIndices.indexOf(tx.indexInHistory) >= 0;
        var isSelected = SelectedTransactionIndex == tx.indexInHistory;
        trClass = isHighlighted || isSelected ? "tr-highlight" : "";
        deltaClass = tx.delta > 0 ? "delta-positive" : "delta-negative";

        if (isHighlighted && !scrolled) {
            scrolled = true;
            scrollToId = "scoll-in-table";
        }

        newHTML += `
            <tr id="` + scrollToId + `" class="` + trClass + `" onClick="onTransactionClicked(` + tx.indexInHistory + `)">
                <td>` + tx.date.toDateString() + `</td>
                <td>` + tx.account + `</td>
                <td>` + tx.desc.split('\n').map(line => "<div>" + line + "</div>").reduce((a, b) => a + b, "") + `</td>
                <td class="` + deltaClass + `">` + tx.delta + `</td>
                <td>` + dp.totalBalance.toFixed(2) + `</td>
            </tr>
        `;
    });

    tableBody.innerHTML = newHTML;
    // document.getElementById("table-scroll").scrollTop = scrollToId == "" ? 0 : document.getElementById(scrollToId).offsetTop;
    if (scrollToId != "")
        document.getElementById(scrollToId).scrollIntoView({behavior: 'smooth'});
}
