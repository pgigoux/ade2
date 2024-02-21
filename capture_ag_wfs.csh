#!/bin/csh
setenv EPICS_CA_ADDR_LIST "172.17.2.37"

set wfs = 'p1'
if ($#argv > 0) then
    set wfs = $argv[1]
endif

set follow =    ( \
                    ag:${wfs}:followA.VALA \
                    ag:${wfs}:followA.VALB \
                    ag:${wfs}:followA.VALC \
                    ag:${wfs}:followA.VALD \
                    ag:${wfs}:followA.VALF \
                    ag:${wfs}:followA.VALH \
                )

set interpol =  ( \
                    ag:${wfs}:interpol.VALA \
                    ag:${wfs}:interpol.VALB \
                    ag:${wfs}:interpol.VALC \
                    ag:${wfs}:interpol.VALD \
                    ag:${wfs}:interpol.VALE \
                    ag:${wfs}:interpol.VALF \
                    ag:${wfs}:interpol.VALG \
                    ag:${wfs}:interpol.VALH \
                    ag:${wfs}:interpol.VALI \
                )

set inpos =     ( \
                   ag:${wfs}:probeinPosition \
                )

camonitor $follow $interpol $inpos
