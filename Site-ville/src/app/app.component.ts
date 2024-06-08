import { Component } from '@angular/core';
import { Router } from "@angular/router";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  constructor(
    protected router: Router,
    ) {}

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
