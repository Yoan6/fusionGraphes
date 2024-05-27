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
  noCitySelected: boolean = false;
  noCityFound: boolean = false;
  graphData: any = null;

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
    this.selectedCity = null;  // Réinitialisation de la ville sélectionnée lors d'une nouvelle recherche
  }

  // Fonction de sélection d'une ville
  selectCity(city: any): void {
    this.city = city.nom;
    this.code_commune = city.code;
    this.departement = city.departement.nom;
    this.selectedCity = city;  // Enregistrement de la ville sélectionnée
    this.citiesList = [];
  }

  // Fonction de soumission du formulaire qui affiche le graphe
  onSubmit() {
    // On vérifie si la ville est sélectionnée
    if (this.city === '') {
      this.noCitySelected = true;
      return;
    }

    // On vérifie que la ville sélectionnée existe
    if (!this.selectedCity || !this.cityService.cityExists(this.city, [this.selectedCity])) {
      this.noCityFound = true;
      this.citiesList = [];  // Vidage de la liste des villes si aucune ville n'est trouvée
      return;
    }

    // On lance le script de génération du graphe
    this.graphService.extract(this.city, this.code_commune, this.departement).subscribe(response => {
      if (response.status === 'success') {
        console.log('Graphe généré avec succès !', response);
        this.graphData = response.data;
        this.showGraph = true;
      } else {
        console.error('Erreur lors de la génération du graphe : ', response.message);
      }
    }, error => {
      console.log('Erreur lors de la génération du graphe : ', error);
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
