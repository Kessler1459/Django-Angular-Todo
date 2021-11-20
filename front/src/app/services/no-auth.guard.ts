import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { map, tap } from 'rxjs/operators';
import { AuthService } from './auth.service';

@Injectable({
    providedIn: 'root'
})
export class NoAuthGuard implements CanActivate {
    constructor(private authService: AuthService, private router: Router) { }

    canActivate() {
        return this.authService.isloggedIn().pipe(
            map(res => res ? this.router.parseUrl("") : true)
        )
    }

}