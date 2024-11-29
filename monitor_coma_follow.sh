#!/bin/csh


while (1)
	set ts = `date +"%Y%m%d-%H:%M:%S"`
	echo "-- $ts --------------------"
	caget -g 10 \
		m2:xPos \
		m2:yPos \
		tcs:m2XUserOffset \
		tcs:m2YUserOffset \
		tcs:om:m2RawXPos \
		tcs:om:m2RawYPos \
		tcs:om:m2XYErr.VALA \
		tcs:om:m2XYErr.VALB \
		tcs:m2XErrorCorr.VAL \
		tcs:m2YErrorCorr.VAL \
		tcs:om:m2XY.VALA \
		tcs:om:m2XY.VALB \
		tcs:om:m2XY.VALC \
		tcs:om:m2XY.VALD \
		tcs:om:m2XY.VALE \
		tcs:om:m2XY.VALF \
		tcs:om:m2XY.VALG \
		tcs:om:m2XY.VALH \
		tcs:om:m2XY.VALI \
		tcs:om:m2XY.VALJ \
		tcs:drives:driveM2S.VALA \
		tcs:drives:driveM2S.VALB \
		tcs:drives:driveM2S.VALC \
		tcs:drives:driveM2S.VALD \
		tcs:drives:driveM2S.VALE \
		tcs:drives:driveM2S.VALF \
		tcs:drives:driveM2S.VALG \
		tcs:drives:driveM2S.VALH \
		tcs:drives:driveM2S.VALI
	sleep 2
end
