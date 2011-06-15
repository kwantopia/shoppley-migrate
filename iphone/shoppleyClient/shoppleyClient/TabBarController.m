//
//  TabBarController.m
//  shoppleyClient
//
//  Created by yod on 6/13/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "TabBarController.h"

@implementation TabBarController

- (void)viewDidLoad {
	[self setTabURLs:[NSArray arrayWithObjects:
					  @"shoppley://current_offers",
					  @"shoppley://redeemed_offers",
					  @"shoppley://summary",
                      nil]];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    UINavigationController* current_tab = [self.viewControllers objectAtIndex:[self selectedIndex]];
    for(UINavigationController* controller in self.viewControllers) {
        if (controller != current_tab) {
            [controller popToRootViewControllerAnimated:NO];
        }
    }
}

@end
