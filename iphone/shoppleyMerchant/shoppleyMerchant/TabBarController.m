//
//  TabBarController.m
//  shoppleyMerchant
//
//  Created by yod on 6/13/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "TabBarController.h"

@implementation TabBarController

- (void)dealloc {
    [super dealloc];
}

- (void)viewDidLoad {
	[self setTabURLs:[NSArray arrayWithObjects:
                      @"shoppley://active_offers",
                      @"shoppley://past_offers",
					  @"shoppley://redeem",
                      @"shoppley://summary",
					  @"shoppley://settings",
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
