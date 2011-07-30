//
//  OffersViewController.h
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SLDataController.h"

@interface OffersViewController : TTTableViewController <SLDataDownloaderDelegate>  {
    NSArray* _offersSections;
}

@end
