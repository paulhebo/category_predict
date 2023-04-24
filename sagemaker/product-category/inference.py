import os
import json
import warnings
import torch
import numpy as np
from pc_model import PCModel, mk_tensors
from transformers import AutoTokenizer

warnings.filterwarnings("ignore",category=FutureWarning)

i2cat=['A/V Accessories', 'AR/VR', 'Access Control Products', 'Active Components', 'Apparel & Textile Manufacturing Equipment', 'Apparel Display & Packaging Supplies','Art & Craft Supplies', 'Auto Electronics', 'Auto Safety & Security', 'Automotive Tools & Equipment', 'BBQ Supplies', 'Baby & Childrens Bedding & Furniture','Baby & Childrens Clothing', 'Baby & Childrens Fashion Goods & Accessories', 'Baby & Childrens Footwear', 'Baby Activity & Gear', 'Baby Care Products', 'Bags & Luggage', 'Barware', 'Batteries & Power Supplies', 'Beauty Treatment & Salon Supplies', 'Bikes & Skates', 'Building Mechanical & Electrical Equipment', 'Building Supplies', 'Burial, Cremation & Ash Storage', 'Business Services', 'Cameras & Accessories', 'Camping & Leisure', 'Commercial Power Systems', 'Communication & Telecom', 'Computer & Laptop Accessories', 'Computer Subsystems', 'Computers & Laptops', 'Corporate & Industrial Wear', 'Corporate & Promotional Gifts', 'Decorative Accents', 'Dentistry Equipment & Supplies', 'Digital Signage', 'Disposable Ware', 'Drinkware', 'Drones, Accessories & Parts', 'Electromechanical Components', 'Electronic Production Equipment & Supplies', 'Electronics Manufacturing Equipment', 'Energy Management', 'Environmental Equipment', 'Eyewear', 'Fabric & Textile Supplies', 'Facility & Management Security Systems', 'Festival & Occasional Gifts', 'Fiber & Yarn', 'Financial Equipment', 'Fireplaces & Accessories', 'Fitness Equipment & Accessories', 'Food & Beverage', 'Games & Hobbies', 'Gaming', 'General Hardware', 'Gift & Retail Packaging', 'Hardware Tooling', 'Health & Wellness', 'Holiday Decorations & Party Supplies', 'Home & Garden Furniture', 'Home Audio', 'Home Fragrance & Aroma', 'Home Textiles & Beddings', 'Hospital & Ward Supplies', 'Household Appliances', 'Household Storage & Organizers', 'Household Supplies', 'Industrial Components', 'Industrial Measuring, Testing & Inspection', 'Industrial Products', 'Industrial Safety & Law Enforcement', 'Interconnects', 'Jewelry & Watches', 'Kitchen Appliances', 'Kitchenware', 'LED & Energy-efficient Lighting', 'LEDs & Optoelectronics', 'Lawn & Garden', 'Lighting & Electricals', 'MP3 Player Accessories', 'Machinery', 'Makeup & Cosmetics', 'Manufacturing Equipment', 'Material Handling & Construction Machinery', 'Medical & Healthcare', 'Mens & Womens Fashion Accessories', 'Mens & Womens Footwear', 'Mens Apparel', 'Mobile Devices', 'Mobile Phone Accessories & Parts', 'Networking Products', 'Non-Fabric Materials', 'Notions & Trims', 'Office & Commercial Furniture', 'Office Electronics', 'Operating Room & Surgical Supplies', 'Outdoor Electronics', 'PCB & Manufacturing Supplies', 'Passive Components', 'Personal Hygiene & Grooming', 'Pet Supplies', 'Printing & Packaging Supplies', 'Rehabilitation & Physiotherapy Supplies', 'Retail Loss Prevention & Security Systems', 'Robotics', 'Safety & Emergency Systems', 'Sanitary Ware & Plumbing', 'Scarves, Shawls & Gloves', 'Security Cameras & Surveillance Products', 'Service Equipment', 'Smart Entertainment', 'Smart Home Security', 'Smoking Gifts & Accessories', 'Specialty Apparel & Rainwear', 'Sporting Goods', 'Sportswear', 'Stage & Sound Equipment', 'Stationery Supplies', 'Swimwear & Beachwear', 'TVs & Video', 'Tablet Accessories & Parts', 'Tableware', 'Tech Gifts & Gadgets', 'Tools & Accessories', 'Toys', 'Underwear & Sleepwear', 'Vehicle Accessories', 'Vehicle Parts', 'Vehicles', 'Water Sports Equipment', 'Wearable Electronics', 'Wedding Apparel', 'Womens Apparel']

num_classes = len(i2cat)

def predict(txt, pcmodel, tokenizer):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_ids, attention_mask = mk_tensors(txt, tokenizer, 128)
    input_ids, attention_mask = input_ids.to(device), attention_mask.to(device)
    logits = pcmodel(input_ids, attention_mask)[0]
    scores = torch.sigmoid(logits)
    return scores.cpu().detach().numpy()


def model_fn(model_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = PCModel.load_from_checkpoint(os.path.join(model_dir, "keyword_epoch_1_v3.ckpt"))
    model.eval()    
    
    return model.to(device)


def predict_fn(input_data, model):
    """
    Apply model to the incoming request
    """

    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased")

    data = input_data['inputs']

    if(torch.cuda.is_available()):
        device = torch.device(f'cuda:{0}')
    else:
        device = torch.device('cpu')
        
    scores = predict(data, model, tokenizer)
            
    top_scores = sorted(scores, reverse=True)[: 3]
    top_icats = np.argsort(-scores)[: 3]
    result = {}
    for i, score in zip(top_icats, top_scores):
        result[i2cat[int(i)]] = float(score)

    result =  {
        'result':result
    }

    return result

def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input
    """
    
    if request_content_type == "application/json":
        request = json.loads(request_body)
    else:
        request = request_body

    return request

def output_fn(prediction, response_content_type):
    """
    Serialize and prepare the prediction output
    """
    
    if response_content_type == "application/json":
        response = json.dumps(prediction)
    else:
        response = str(prediction)

    return response