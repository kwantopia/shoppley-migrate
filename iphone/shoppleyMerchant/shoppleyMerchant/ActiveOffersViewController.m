//
//  ActiveOffersViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/13/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "ActiveOffersViewController.h"

#import "SLActiveOffer.h"
#import "SLNewOffer.h"
#import "SLTableViewDataSource.h"

@implementation ActiveOffersViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.title = @"Active Offers";
        self.tabBarItem = [[[UITabBarItem alloc] initWithTitle:self.title image:[UIImage imageNamed:@"tab_active_offers.png"] tag:0] autorelease];
        
        self.tableViewStyle = UITableViewStylePlain;
        self.variableHeightRows = YES;
        
        self.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"New Offer..." style:UIBarButtonItemStyleBordered target:self action:@selector(newOffer)] autorelease];
    }
    return self;
}

- (void)createModel {
    _offers = [[[SLDataController sharedInstance] obtainActiveOffersWithDelegate:self forcedDownload:NO] retain];
    
    if (_offers) {
        TTDPRINT(@"%@", _offers);
        NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
        for (int i = 0; i < [_offers count]; i++) {
            SLActiveOffer* offer = [_offers objectAtIndex:i];
            [items addObject:[SLActiveOfferTableItem itemWithOffer:offer URL:nil]];
        }
        self.dataSource = [SLListDataSource dataSourceWithItems:items];
    } else {
        self.dataSource = [TTListDataSource dataSourceWithObjects:
                           [TTTableActivityItem itemWithText:@"Processing..."],
                           nil];
    }
}

- (void)newOffer {
    TTURLAction *urlAction = [[[TTURLAction alloc] initWithURLPath:@"shoppley://offer/new"] autorelease];
    urlAction.query = [NSDictionary dictionaryWithObject:[[[SLNewOffer alloc] init] autorelease] forKey:@"offer"];
    urlAction.animated = YES;
    [[TTNavigator navigator] openURLAction:urlAction];
}

@end
