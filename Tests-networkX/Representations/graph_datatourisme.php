<?php
// composer autoload
require '../vendor/autoload.php';

// instanciation du client
$api = \Datatourisme\Api\DatatourismeApi::create('http://localhost:9999/blazegraph/namespace/kb/sparql');

// éxecution d'une requête
$result = $api->process('
    {
      poi (
        from: 0,
        size: 20,
      ) 
      {
        total
        results {
          _uri
          dc_identifier
          rdfs_label
          rdf_type
          isLocatedAt {
            schema_address {
              schema_postalCode
            }
          }
        }
      }
    }
    ');

// prévisualisation des résultats
var_dump($result);
?>