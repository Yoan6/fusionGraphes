import { Component, OnInit } from '@angular/core';
import { CityService } from 'src/app/Services/city.service';
import { GraphService } from 'src/app/Services/graph.service';
import { Observable, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, tap } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title: string = 'Site d\'information des villes de France';

  city: string = '';
  code_commune: string = '';
  departement: string = '';

  selectedCity: any = null;  // Variable pour stocker la ville sélectionnée
  showGraph: boolean = false;
  private searchTerms = new Subject<string>();
  cities$: Observable<any[]> = new Observable<any[]>();
  citiesList: any[] = [];
  noCitySelected: boolean = false;  // Aucune ville sélectionnée
  noCityFound: boolean = false;   // Aucune ville trouvée
  is_a_toponyme: boolean = false;   // Ville trouvée est un toponyme (existe avec le même nom dans plusieurs départements)
  graphData: any = null;
  loading: boolean = false;

  constructor(
    private cityService: CityService,
    private graphService: GraphService,
    ) {}

  ngOnInit() {
    this.cities$ = this.searchTerms.pipe(
      debounceTime(100), // Attendre 100ms après chaque frappe avant de lancer la recherche
      distinctUntilChanged(), // Ignorer le terme de recherche si c'est le même que le précédent
      switchMap((term: string) => this.cityService.searchCities(term).pipe(
        tap(cities => {
          this.citiesList = cities;
          if (cities.length === 0) {
            this.noCityFound = true;
          } else {
            this.noCityFound = false;
          }
        })
      ))
    );
    this.cities$.subscribe();
  }

  // Fonction de recherche des villes
  search(term: string): void {
    this.searchTerms.next(term);
    this.noCitySelected = false;
    this.noCityFound = false;
    this.is_a_toponyme = false;
    this.selectedCity = null;  // Réinitialisation de la ville sélectionnée lors d'une nouvelle recherche
  }

  // Fonction de sélection d'une ville
  selectCity(city: any): void {
    this.is_a_toponyme = this.isToponyme(city);

    // Si la ville est un toponyme, on affiche le département
    if (this.is_a_toponyme) {
      this.city = city.nom + ' (' + city.departement.nom + ')';
    } else {
      this.city = city.nom;
    }

    this.code_commune = city.code;
    this.departement = city.departement.nom;
    this.selectedCity = city;  // Enregistrement de la ville sélectionnée
    this.citiesList = [];
  }

  // Permet de savoir si une ville est toponyme parmi la liste des villes
  isToponyme(city: any): boolean {
    let matchingCities = this.citiesList.filter((c: { nom: string; }) => c.nom.toLowerCase() === city.nom.toLowerCase());
    if (matchingCities.length > 1) {
      return true;
    }
    return false;
  }

  // Fonction de soumission du formulaire qui affiche le graphe
  onSubmit() {
    // Si aucune ville n'est sélectionnée
    if (this.city === '') {
      this.noCitySelected = true;
      return;
    }

    // On vérifie si la ville saisie correspond à une ville existante
    const cityName = this.city.split(' (')[0];
    this.cityService.searchCities(cityName).subscribe(cities => {
      const matchingCities = cities.filter((c: { nom: string; }) => c.nom.toLowerCase() === cityName.toLowerCase());

      // Si aucune ville correspondante n'est trouvée
      if (matchingCities.length === 0) {
        this.noCityFound = true;
        this.citiesList = [];
        return;
      }

      // Vérifier si la ville saisie est un toponyme sans être sélectionnée
      if (matchingCities.length > 1 && !this.selectedCity) {
        this.is_a_toponyme = true;
        return;
      }

      // Ville correspondante trouvée et pas un toponyme ou toponyme sélectionné
      let matchingCity: any;
      if (this.selectedCity) {
        matchingCity = matchingCities.find((c: { code: string; }) => c.code === this.selectedCity.code);
      }
      else {
        matchingCity = matchingCities[0];
      }

      this.noCityFound = false;
      this.is_a_toponyme = false;
      this.loading = true;
      this.code_commune = matchingCity.code;
      this.departement = matchingCity.departement.nom;
      this.citiesList = [];

      // Si la ville sélectionnée est un toponyme, on affiche le département
      if (matchingCities.length > 1) {
        this.city = `${matchingCity.nom} (${matchingCity.departement.nom})`;
      } else {
        this.city = matchingCity.nom;
      }
      this.generateGraph();
    }, error => {
      console.log('Erreur lors de la vérification de la ville : ', error);
      this.loading = false;
    });
  }


  generateGraph() {
    this.is_a_toponyme = false;
    this.loading = true;
    const cityName = this.city.split(' (')[0];    // Afin d'empècher les erreurs de toponymes
    // On lance le script de génération du graphe
    this.graphService.extract(cityName, this.code_commune, this.departement).subscribe(response => {
      if (response.status === 'success') {
        console.log('Graphe généré avec succès !', response);
        this.loading = false;
        this.graphData = response.data;
        this.showGraph = true;
      } else {
        console.error('Erreur lors de la génération du graphe : ', response.message);
        this.loading = false;
        this.noCityFound = true;
      }
    }, error => {
      console.log('Erreur lors de la génération du graphe : ', error);
      this.loading = false;
    });
  }

  /*exportSite() {
    if (this.city === '' || !this.selectedCity) {
      this.noCitySelected = true;
      return;
    }

    this.graphService.exportSite(this.city, this.selectedCity.code, this.selectedCity.departement.nom).subscribe((response: { body: BlobPart; }) => {
      const blob = new Blob([response.body], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'site_local.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }, (error: any) => {
      console.log('Erreur lors de l\'exportation du site', error);
    });
  }*/
}
