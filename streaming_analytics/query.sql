SELECT 
    System.Timestamp AS WindowEnd,
    COUNT(*) AS DeviceCount
into StreamingDeviceCount
FROM SaInputName 
GROUP BY
    TumblingWindow(Duration(second, 10))


SELECT System.Timestamp AS WindowEnd, COUNT(*) AS DeviceCount into StreamingDeviceCount FROM SaInputName GROUP BY TumblingWindow(Duration(second, 10))

SELECT 
    deviceId,
    COUNT(*) AS DeviceCount,
    System.Timestamp() AS Window_end
INTO StreamingIndividualDeviceCount
FROM SaInputName 
GROUP BY
    deviceId,
    HoppingWindow(second, 60, 10)