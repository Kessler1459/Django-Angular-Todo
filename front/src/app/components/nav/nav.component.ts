import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { User } from 'src/app/models/user';
import { AuthService } from 'src/app/services/auth.service';

@Component({
    selector: 'app-nav',
    templateUrl: './nav.component.html',
    styleUrls: ['./nav.component.scss']
})
export class NavComponent implements OnInit {
    user:User;
    constructor(public authService: AuthService,private router:Router) { }

    ngOnInit(): void {
        if(this.authService.token){
            this.authService.getAuthUser().subscribe(user=>this.user=user)
        }
    }

    logout() {
        this.authService.logout().subscribe(()=>this.router.navigateByUrl("/login"))
    }

}
