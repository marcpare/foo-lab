
<?php

// Need:
// username for URL
// API key

$curl = curl_init('https://marcpare.wufoo.com/api/v3/forms.xml');       //1
curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);                          //2
curl_setopt($curl, CURLOPT_USERPWD, 'ADGZ-9NNW-1U81-LVXA:footastic');   //3
curl_setopt($curl, CURLOPT_HTTPAUTH, CURLAUTH_ANY);                     //4
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);                          
curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);                           
curl_setopt($curl, CURLOPT_USERAGENT, 'Testing for Wufoo API Contest');             //5

$response = curl_exec($curl);                                           //6
$resultStatus = curl_getinfo($curl);                                    //7

if($resultStatus['http_code'] == 200) {                     //8
    echo htmlentities($response);
} else {
    echo 'Call Failed '.print_r($resultStatus);                         //9
}
?>